"""
CV-Craft-Studio - Resume Analytics Dashboard
Session-based analytics computed from resume content. No paid service.
"""

from typing import Dict, List, Tuple
import re
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# TEXT ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────

def compute_text_analytics(text: str) -> Dict:
    """Compute rich analytics from raw resume text."""
    if not text.strip():
        return {}

    words = re.findall(r'\b[a-zA-Z]+\b', text)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    word_count = len(words)
    sentence_count = max(1, len(sentences))
    avg_words_per_sentence = word_count / sentence_count

    # Word frequency (top 20 meaningful words)
    stopwords = {'the','and','or','but','in','on','at','to','for','of','with','by',
                 'from','is','are','was','were','be','been','have','has','had','a','an'}
    freq = {}
    for w in words:
        w_low = w.lower()
        if w_low not in stopwords and len(w_low) > 3:
            freq[w_low] = freq.get(w_low, 0) + 1
    top_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:20]

    # Action verb detection
    action_verbs = [
        'analyzed', 'designed', 'developed', 'implemented', 'optimized',
        'led', 'managed', 'built', 'created', 'improved', 'reduced', 'increased',
        'delivered', 'launched', 'automated', 'streamlined', 'coordinated',
        'presented', 'trained', 'mentored', 'executed', 'deployed', 'integrated',
    ]
    verb_count = sum(1 for w in words if w.lower() in action_verbs)
    verb_pct = round(verb_count / max(1, word_count) * 100, 1)

    # Quantified lines (lines with numbers/percentages)
    quant_lines = [l for l in lines if re.search(r'\d+[%+KMB]?|\$\d+', l)]
    quant_pct = round(len(quant_lines) / max(1, len(lines)) * 100, 1)

    # Sentence length distribution
    sentence_lengths = [len(s.split()) for s in sentences]
    long_sentences = [s for s in sentence_lengths if s > 30]
    short_sentences = [s for s in sentence_lengths if s < 5]

    # Readability estimate (simple Flesch approximation)
    syllables = sum(_count_syllables(w) for w in words)
    if sentence_count > 0 and word_count > 0:
        flesch = 206.835 - 1.015*(word_count/sentence_count) - 84.6*(syllables/word_count)
        flesch = max(0, min(100, flesch))
    else:
        flesch = 0

    readability_label = (
        'Very Easy' if flesch >= 80 else
        'Easy'      if flesch >= 65 else
        'Standard'  if flesch >= 50 else
        'Fairly Difficult' if flesch >= 35 else
        'Difficult'
    )

    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'line_count': len(lines),
        'avg_words_per_sentence': round(avg_words_per_sentence, 1),
        'top_words': top_words,
        'action_verb_count': verb_count,
        'action_verb_pct': verb_pct,
        'quantified_lines': len(quant_lines),
        'quantified_pct': quant_pct,
        'long_sentences': len(long_sentences),
        'short_sentences': len(short_sentences),
        'flesch_score': round(flesch, 1),
        'readability_label': readability_label,
        'char_count': len(text),
        'unique_words': len(set(w.lower() for w in words)),
        'vocabulary_richness': round(len(set(w.lower() for w in words)) / max(1, word_count) * 100, 1),
    }


def _count_syllables(word: str) -> int:
    """Approximate syllable count for a word."""
    word = word.lower().strip(".,!?;:")
    if len(word) <= 3:
        return 1
    count = len(re.findall(r'[aeiou]+', word))
    if word.endswith('e'):
        count = max(1, count - 1)
    return max(1, count)


def compute_section_analytics(resume_data: Dict) -> Dict:
    """Compute analytics per resume section."""
    result = {}
    sections_to_check = [
        ('experience', 'Work Experience'),
        ('internships', 'Internships'),
        ('projects', 'Projects'),
    ]
    for key, label in sections_to_check:
        items = resume_data.get(key, [])
        if not items:
            continue
        bullets_total = sum(len(item.get('bullets', [])) for item in items)
        all_bullets = [b for item in items for b in item.get('bullets', [])]
        quantified = sum(1 for b in all_bullets if re.search(r'\d+[%+KMB]?|\$\d+', b))
        action_verb_bullets = sum(1 for b in all_bullets if _starts_with_action_verb(b))
        result[key] = {
            'label': label,
            'item_count': len(items),
            'total_bullets': bullets_total,
            'quantified_bullets': quantified,
            'action_verb_bullets': action_verb_bullets,
            'avg_bullets_per_item': round(bullets_total / max(1, len(items)), 1),
            'quantification_rate': round(quantified / max(1, bullets_total) * 100, 1),
            'action_verb_rate': round(action_verb_bullets / max(1, bullets_total) * 100, 1),
        }
    return result


def _starts_with_action_verb(bullet: str) -> bool:
    action_verbs = {
        'analyzed','designed','developed','implemented','optimized','automated',
        'led','managed','built','created','improved','reduced','increased','delivered',
        'launched','streamlined','coordinated','presented','trained','mentored',
        'executed','deployed','integrated','established','spearheaded','transformed',
        'researched','evaluated','identified','facilitated','orchestrated','generated',
    }
    first_word = re.match(r'^[•\-\*]?\s*([a-zA-Z]+)', bullet.strip())
    if first_word:
        return first_word.group(1).lower() in action_verbs
    return False


# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY CHART BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

BG = 'rgba(0,0,0,0)'
FONT_COLOR = '#1F2937'
GRID_COLOR = 'rgba(255,255,255,0.06)'


def chart_word_frequency(top_words: List[Tuple[str, int]]) -> go.Figure:
    """Horizontal bar chart of top words."""
    if not top_words:
        return go.Figure()
    words, counts = zip(*top_words[:15])
    colors = [f'rgba(255,153,51,{0.4 + 0.04*i})' for i in range(len(words))]
    fig = go.Figure(go.Bar(
        x=list(counts), y=list(words),
        orientation='h',
        marker=dict(color=list(reversed(colors)), line=dict(width=0)),
        text=[str(c) for c in counts],
        textposition='outside',
        textfont=dict(color=FONT_COLOR, size=11),
        hovertemplate='<b>%{y}</b>: %{x} occurrences<extra></extra>',
    ))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=FONT_COLOR, family='Inter'),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, autorange='reversed',
                   tickfont=dict(size=12)),
        height=380, margin=dict(t=10, b=10, l=10, r=60),
        bargap=0.25,
    )
    return fig


def chart_bullet_quality(section_analytics: Dict) -> go.Figure:
    """Grouped bar chart: quantified vs action-verb bullets by section."""
    if not section_analytics:
        return go.Figure()
    labels = [v['label'] for v in section_analytics.values()]
    quant  = [v['quantification_rate'] for v in section_analytics.values()]
    verbs  = [v['action_verb_rate'] for v in section_analytics.values()]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Quantified Bullets %', x=labels, y=quant,
        marker_color='rgba(21,128,61,0.75)',
        text=[f'{q:.0f}%' for q in quant], textposition='outside',
        textfont=dict(color=FONT_COLOR),
    ))
    fig.add_trace(go.Bar(
        name='Action Verb Bullets %', x=labels, y=verbs,
        marker_color='rgba(255,153,51,0.75)',
        text=[f'{v:.0f}%' for v in verbs], textposition='outside',
        textfont=dict(color=FONT_COLOR),
    ))
    fig.update_layout(
        barmode='group',
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=FONT_COLOR, family='Inter'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR,
                   ticksuffix='%', range=[0, 110]),
        legend=dict(font=dict(color=FONT_COLOR), bgcolor='rgba(0,0,0,0)'),
        height=280, margin=dict(t=20, b=20, l=20, r=20),
        bargap=0.25,
    )
    return fig


def chart_readability_gauge(flesch_score: float) -> go.Figure:
    """Gauge chart for readability score."""
    color = ('#15803D' if flesch_score >= 65 else
             '#B45309' if flesch_score >= 45 else '#B91C1C')
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=flesch_score,
        title={'text': 'Readability (Flesch)', 'font': {'size': 14, 'color': FONT_COLOR}},
        number={'font': {'size': 28, 'color': color}, 'suffix': '/100'},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#888',
                     'tickfont': {'color': '#888', 'size': 10}},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': '#FFF4E6',
            'borderwidth': 0,
            'steps': [
                {'range': [0,  45], 'color': 'rgba(185,28,28,0.15)'},
                {'range': [45, 65], 'color': 'rgba(180,83,9,0.15)'},
                {'range': [65,100], 'color': 'rgba(21,128,61,0.15)'},
            ],
        }
    ))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=FONT_COLOR),
        height=200, margin=dict(t=50, b=10, l=30, r=30),
    )
    return fig


def chart_section_coverage(resume_data: Dict) -> go.Figure:
    """Radar/spider chart of resume section completeness."""
    categories = ['Contact', 'Summary', 'Education', 'Experience', 'Skills', 'Certs', 'Projects']
    values = [
        1 if resume_data.get('personal', {}).get('name') else 0,
        1 if resume_data.get('summary') else 0,
        min(1, len(resume_data.get('education', [])) / 1),
        min(1, len(resume_data.get('experience', []) or resume_data.get('internships', [])) / 1),
        1 if resume_data.get('skills') else 0,
        min(1, len(resume_data.get('certifications', [])) / 1),
        min(1, len(resume_data.get('projects', [])) / 1),
    ]
    values_pct = [v * 100 for v in values]
    values_pct_closed = values_pct + [values_pct[0]]  # close the loop
    categories_closed = categories + [categories[0]]

    fig = go.Figure(go.Scatterpolar(
        r=values_pct_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(255,153,51,0.15)',
        line=dict(color='rgba(255,153,51,0.8)', width=2),
        marker=dict(size=7, color='#FF9933'),
        hovertemplate='<b>%{theta}</b>: %{r:.0f}%<extra></extra>',
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(30,42,58,0.5)',
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(color='#888', size=9),
                gridcolor='rgba(255,255,255,0.08)',
                linecolor='rgba(255,255,255,0.08)',
                ticksuffix='%',
            ),
            angularaxis=dict(
                tickfont=dict(color=FONT_COLOR, size=11),
                gridcolor='rgba(255,255,255,0.08)',
                linecolor='rgba(255,255,255,0.08)',
            ),
        ),
        paper_bgcolor=BG,
        font=dict(color=FONT_COLOR, family='Inter'),
        height=320, margin=dict(t=20, b=20, l=30, r=30),
    )
    return fig
