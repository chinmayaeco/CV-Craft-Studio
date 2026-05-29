"""
CV-Craft-Studio - Role Profiles
Predefined keyword/skill profiles for 13 common roles.
"""

ROLE_PROFILES = {
    'Data Analyst': {
        'keywords': [
            'data analysis', 'sql', 'python', 'excel', 'tableau', 'power bi',
            'data visualization', 'statistical analysis', 'data cleaning', 'etl',
            'business intelligence', 'dashboard', 'reporting', 'kpi', 'metrics',
            'hypothesis testing', 'regression analysis', 'data modeling'
        ],
        'tools': ['Python', 'SQL', 'Excel', 'Tableau', 'Power BI', 'R', 'Pandas', 'NumPy', 'Matplotlib'],
        'focus_areas': [
            'Data cleaning and preparation skills',
            'Strong SQL proficiency',
            'Data visualization experience',
            'Business problem-solving orientation',
            'Statistical methodology'
        ],
        'common_mistakes': [
            'Listing tools without showing how they were used',
            'No quantified business impact from analyses',
            'Missing domain knowledge (finance, marketing, etc.)',
            'Weak descriptions of analytical methodology',
        ],
        'bullet_examples': [
            'Analyzed [N] customer transaction records using SQL and Python to identify churn patterns, reducing attrition by [X%].',
            'Developed interactive Power BI dashboard tracking [N] KPIs, used by [N] stakeholders for weekly reporting.',
            'Cleaned and transformed [N] rows of raw data using Pandas, improving model accuracy by [X%].',
        ]
    },
    'Business Analyst': {
        'keywords': [
            'business analysis', 'requirements gathering', 'stakeholder management',
            'process improvement', 'user stories', 'use cases', 'brd', 'frd',
            'gap analysis', 'as-is to-be', 'agile', 'scrum', 'project management',
            'data analysis', 'sql', 'excel', 'business intelligence', 'kpi'
        ],
        'tools': ['Jira', 'Confluence', 'SQL', 'Excel', 'Visio', 'Tableau', 'Power BI', 'MS Project'],
        'focus_areas': [
            'Requirements elicitation and documentation',
            'Stakeholder communication skills',
            'Process mapping and improvement',
            'Data-driven decision making',
            'Bridge between business and technology'
        ],
        'common_mistakes': [
            'Too technical — business context is key',
            'No mention of stakeholder management',
            'Missing process improvement outcomes',
            'No examples of requirements documentation',
        ],
        'bullet_examples': [
            'Gathered and documented requirements from [N] stakeholders, producing BRD that reduced development rework by [X%].',
            'Mapped AS-IS to TO-BE processes, identifying [N] improvement opportunities saving [X hours/month].',
            'Led [N] sprint ceremonies as Scrum Master, improving team velocity by [X%] over [N] sprints.',
        ]
    },
    'HR Analyst': {
        'keywords': [
            'hr analytics', 'people analytics', 'workforce planning', 'attrition analysis',
            'recruitment metrics', 'hris', 'talent acquisition', 'compensation analysis',
            'performance management', 'employee engagement', 'hr reporting', 'headcount'
        ],
        'tools': ['Excel', 'Power BI', 'Tableau', 'SAP HR', 'Workday', 'SQL', 'Python', 'R'],
        'focus_areas': [
            'HR metrics and KPI tracking',
            'Attrition/retention analysis',
            'Compensation benchmarking',
            'Data-driven HR decision making',
        ],
        'common_mistakes': [
            'No quantified HR impact',
            'Missing specific HRIS tool experience',
            'Weak analytical skills demonstration',
        ],
        'bullet_examples': [
            'Analyzed employee attrition data for [N] employees, identifying top [N] drivers and reducing turnover by [X%].',
            'Built HR dashboard tracking [N] metrics including headcount, attrition, and time-to-hire using Power BI.',
        ]
    },
    'Finance Analyst': {
        'keywords': [
            'financial modeling', 'financial analysis', 'forecasting', 'budgeting',
            'variance analysis', 'p&l', 'balance sheet', 'cash flow', 'dcf', 'npv',
            'irr', 'excel', 'financial reporting', 'cost analysis', 'revenue analysis'
        ],
        'tools': ['Excel', 'SAP', 'Oracle', 'Power BI', 'Tableau', 'Bloomberg', 'Python'],
        'focus_areas': [
            'Financial modeling and valuation',
            'Budgeting and forecasting',
            'Management reporting',
            'Cost-benefit analysis',
        ],
        'common_mistakes': [
            'Missing specific financial modeling experience',
            'No mention of financial tools (SAP, Oracle)',
            'Weak quantification of financial impact',
        ],
        'bullet_examples': [
            'Built 3-statement financial model for [company/project] enabling [N] investment scenarios analysis.',
            'Prepared monthly variance analysis comparing actuals vs. budget for [N] cost centers, presenting to CFO.',
        ]
    },
    'Marketing Analyst': {
        'keywords': [
            'marketing analytics', 'digital marketing', 'campaign analysis', 'seo', 'sem',
            'google analytics', 'social media analytics', 'roi analysis', 'a/b testing',
            'customer segmentation', 'market research', 'brand analytics', 'ctr', 'cpa'
        ],
        'tools': ['Google Analytics', 'Excel', 'Tableau', 'Salesforce', 'HubSpot', 'SQL', 'Python'],
        'focus_areas': [
            'Campaign performance analysis',
            'Customer segmentation',
            'ROI measurement',
            'Digital channel analytics',
        ],
        'common_mistakes': [
            'No campaign metrics (CTR, CPA, ROAS)',
            'Missing digital analytics tools',
            'Weak customer insight demonstration',
        ],
        'bullet_examples': [
            'Analyzed [N] digital campaigns achieving [X%] improvement in CTR and [X%] reduction in CPA.',
            'Segmented customer base of [N] users into [N] personas, improving email open rate by [X%].',
        ]
    },
    'Operations Analyst': {
        'keywords': [
            'operations analysis', 'process improvement', 'supply chain', 'logistics',
            'lean', 'six sigma', 'operational efficiency', 'capacity planning', 'inventory',
            'kpi', 'workflow optimization', 'cost reduction', 'vendor management'
        ],
        'tools': ['Excel', 'SAP', 'Oracle', 'Tableau', 'Power BI', 'SQL', 'Visio'],
        'focus_areas': [
            'Process optimization',
            'Cost reduction initiatives',
            'Supply chain analytics',
            'Operational KPI tracking',
        ],
        'common_mistakes': [
            'No quantified efficiency gains',
            'Missing process improvement methodology (Lean/Six Sigma)',
            'Weak supply chain domain knowledge',
        ],
        'bullet_examples': [
            'Redesigned [process name] workflow, reducing cycle time by [X%] and saving [X hours/week].',
            'Conducted root cause analysis on [N] operational bottlenecks, implementing solutions that cut costs by [X%].',
        ]
    },
    'Product Manager': {
        'keywords': [
            'product management', 'product roadmap', 'product strategy', 'user stories',
            'agile', 'scrum', 'go-to-market', 'product launch', 'stakeholder management',
            'product analytics', 'a/b testing', 'customer research', 'ux', 'mvp'
        ],
        'tools': ['Jira', 'Confluence', 'Trello', 'Figma', 'Mixpanel', 'SQL', 'Tableau'],
        'focus_areas': [
            'Product vision and strategy',
            'Cross-functional team leadership',
            'Customer-centric thinking',
            'Data-driven product decisions',
        ],
        'common_mistakes': [
            'Too feature-focused instead of outcome-focused',
            'No mention of business impact of products',
            'Missing customer research experience',
        ],
        'bullet_examples': [
            'Launched [product/feature] used by [N] users, achieving [X%] increase in [key metric].',
            'Defined and prioritized product roadmap of [N] features, delivering [X] releases in [timeframe].',
        ]
    },
    'Machine Learning Engineer': {
        'keywords': [
            'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow',
            'pytorch', 'scikit-learn', 'model deployment', 'mlops', 'feature engineering',
            'python', 'sql', 'docker', 'aws', 'model evaluation', 'neural networks'
        ],
        'tools': ['Python', 'TensorFlow', 'PyTorch', 'scikit-learn', 'Docker', 'AWS', 'MLflow', 'Git'],
        'focus_areas': [
            'Model development and deployment',
            'Feature engineering',
            'MLOps and production pipelines',
            'Model evaluation and improvement',
        ],
        'common_mistakes': [
            'Listing algorithms without business context',
            'No model performance metrics',
            'Missing deployment/production experience',
        ],
        'bullet_examples': [
            'Developed [model type] model achieving [X%] accuracy/F1-score on [dataset], deployed to production using [tool].',
            'Built end-to-end ML pipeline processing [N] records/day using [technology stack].',
        ]
    },
    'Consultant': {
        'keywords': [
            'consulting', 'strategy', 'client management', 'problem solving', 'analysis',
            'recommendations', 'stakeholder management', 'project management', 'presentations',
            'business development', 'frameworks', 'deliverables', 'engagement management'
        ],
        'tools': ['Excel', 'PowerPoint', 'SQL', 'Tableau', 'Miro', 'MS Project'],
        'focus_areas': [
            'Structured problem solving',
            'Client communication and presentations',
            'Data-driven recommendations',
            'Project management',
        ],
        'common_mistakes': [
            'Too much jargon, not enough outcomes',
            'No client or business impact',
            'Missing team/stakeholder management',
        ],
        'bullet_examples': [
            'Led [N]-member team in [engagement type] for [client type], delivering [recommendation] resulting in [impact].',
            'Conducted [N] stakeholder interviews to identify [business problem], developing [solution] adopted by [client].',
        ]
    },
    'Research Assistant': {
        'keywords': [
            'research', 'literature review', 'data collection', 'statistical analysis',
            'research design', 'survey design', 'academic writing', 'publications',
            'hypothesis testing', 'quantitative', 'qualitative', 'spss', 'stata', 'r'
        ],
        'tools': ['SPSS', 'Stata', 'R', 'Python', 'NVivo', 'MATLAB', 'LaTeX', 'Mendeley'],
        'focus_areas': [
            'Research methodology',
            'Data analysis (quantitative/qualitative)',
            'Academic writing and publications',
            'Literature synthesis',
        ],
        'common_mistakes': [
            'No mention of research outcomes/publications',
            'Missing methodology details',
            'Weak academic writing examples',
        ],
        'bullet_examples': [
            'Conducted [research type] study on [topic] analyzing [N] data points using [method], published in [journal/conference].',
            'Performed systematic literature review of [N] papers on [topic], synthesizing findings for [purpose].',
        ]
    },
    'Assistant Professor': {
        'keywords': [
            'teaching', 'curriculum development', 'research', 'publications', 'mentoring',
            'course design', 'pedagogy', 'academic advising', 'grants', 'conferences',
            'lecturing', 'seminars', 'peer review', 'academic administration'
        ],
        'tools': ['LMS', 'Moodle', 'Blackboard', 'Canvas', 'SPSS', 'R', 'Python', 'LaTeX'],
        'focus_areas': [
            'Teaching and pedagogy',
            'Research output and publications',
            'Student mentoring and advising',
            'Curriculum development',
        ],
        'common_mistakes': [
            'Missing publication list or research output',
            'No teaching effectiveness data',
            'Weak grant/funding experience mention',
        ],
        'bullet_examples': [
            'Developed and delivered [course name] curriculum for [N] students, achieving [X%] satisfaction score.',
            'Published [N] peer-reviewed papers in [journals], with [N] citations.',
        ]
    },
    'Healthcare Analyst': {
        'keywords': [
            'healthcare analytics', 'clinical data', 'patient outcomes', 'ehr', 'icd codes',
            'healthcare quality', 'hospital operations', 'revenue cycle', 'claims analysis',
            'population health', 'sql', 'excel', 'tableau', 'hipaa', 'healthcare metrics'
        ],
        'tools': ['SQL', 'Excel', 'Tableau', 'Python', 'SAS', 'Epic', 'Cerner', 'Power BI'],
        'focus_areas': [
            'Clinical data analysis',
            'Healthcare quality metrics',
            'Revenue cycle analytics',
            'Population health management',
        ],
        'common_mistakes': [
            'Missing healthcare domain knowledge',
            'No mention of regulatory compliance (HIPAA)',
            'Weak clinical metrics understanding',
        ],
        'bullet_examples': [
            'Analyzed clinical outcomes data for [N] patients to identify [pattern], reducing [complication/cost] by [X%].',
            'Developed healthcare KPI dashboard tracking [N] quality metrics for [department/hospital].',
        ]
    },
    'Management Trainee': {
        'keywords': [
            'management', 'leadership', 'operations', 'cross-functional', 'project management',
            'business analysis', 'stakeholder management', 'strategic planning', 'reporting',
            'problem solving', 'team collaboration', 'communication'
        ],
        'tools': ['Excel', 'PowerPoint', 'SQL', 'Tableau', 'Jira', 'MS Project'],
        'focus_areas': [
            'Cross-functional exposure',
            'Leadership potential',
            'Business acumen',
            'Adaptability and learning agility',
        ],
        'common_mistakes': [
            'Too generic — needs specific examples',
            'Missing business impact examples',
            'No demonstration of leadership potential',
        ],
        'bullet_examples': [
            'Managed cross-functional project involving [N] teams, delivering [outcome] within [timeframe] and [budget].',
            'Developed [report/analysis] used by [N] senior managers for [strategic decision].',
        ]
    },
}


def get_role_profile(role_name: str) -> dict:
    """Get profile for a specific role. Returns empty dict if not found."""
    return ROLE_PROFILES.get(role_name, {})


def get_all_roles() -> list:
    """Get list of all available role names."""
    return list(ROLE_PROFILES.keys())
