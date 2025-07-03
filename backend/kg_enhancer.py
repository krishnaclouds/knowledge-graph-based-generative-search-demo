"""
Knowledge Graph Enhancement Module

This module provides advanced entity extraction and relationship discovery
to enhance the knowledge graph with richer connections between documents.
"""

import logging
import re
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict, Counter
import json

from database import db

logger = logging.getLogger(__name__)

class KnowledgeGraphEnhancer:
    """Enhanced knowledge graph builder with advanced entity extraction and relationship discovery"""
    
    def __init__(self):
        self.entity_patterns = self._load_entity_patterns()
        self.relationship_patterns = self._load_relationship_patterns()
        
    def _load_entity_patterns(self) -> Dict:
        """Load patterns for entity extraction"""
        return {
            'companies': [
                r'\b(Google|Alphabet|Apple|Microsoft|Amazon|Meta|Facebook|Tesla|OpenAI|NVIDIA|Intel|IBM|Oracle|Netflix|Uber|Airbnb|Twitter|LinkedIn|Adobe|Salesforce|Zoom|Spotify|Slack|Dropbox|GitHub|GitLab|Reddit|Discord|TikTok|Snapchat|Pinterest|Square|Stripe|Shopify|Coinbase|Robinhood|DoorDash|Instacart|Peloton|Zoom|DocuSign|Snowflake|Palantir|Unity|Roblox|Epic Games|Valve|Steam|Oculus|Magic Leap|SpaceX|Blue Origin|Waymo|Cruise|Aurora|Argo AI|Mobileye|Qualcomm|AMD|ARM|Broadcom|Cisco|Dell|HP|Lenovo|Huawei|Samsung|LG|Sony|Panasonic|Canon|Nikon|DJI|Boston Dynamics|iRobot|Roomba|Alexa|Siri|Cortana|Watson|DeepMind|Anthropic|Cohere|Stability AI|Midjourney|Runway|Jasper|Copy.ai|Grammarly|Notion|Figma|Canva|Miro|Trello|Asana|Monday|Jira|Confluence|HubSpot|Mailchimp|Constant Contact|Sendinblue|Campaign Monitor|Intercom|Zendesk|Freshworks|ServiceNow|Workday|Okta|Auth0|1Password|LastPass|Bitwarden|NordVPN|ExpressVPN|Surfshark)\b',
                r'\b([A-Z][a-z]+ (?:Inc|Corp|Corporation|LLC|Ltd|Limited|Technologies|Systems|Solutions|Software|Labs|Research|AI|ML|Data|Cloud|Security|Robotics|Automation|Intelligence|Analytics|Platform|Networks|Communications|Media|Entertainment|Gaming|Studios|Productions|Publishing|Broadcasting|Streaming|Content|Creative|Design|Marketing|Advertising|Commerce|Retail|Marketplace|Payments|Financial|Fintech|Banking|Insurance|Healthcare|Medical|Pharmaceutical|Biotech|Genomics|Diagnostics|Therapeutics|Devices|Equipment|Manufacturing|Industrial|Automotive|Aerospace|Defense|Energy|Renewable|Solar|Wind|Nuclear|Oil|Gas|Mining|Agriculture|Food|Beverage|Consumer|Fashion|Beauty|Travel|Hospitality|Real Estate|Construction|Education|Training|Consulting|Services|Logistics|Transportation|Delivery|Shipping))\b'
            ],
            'people': [
                r'\b([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b(?=\s(?:is|was|has|said|stated|announced|developed|created|founded|invented|discovered|published|presented|proposed|argued|claimed|believes|thinks|suggests|recommends|advises|leads|heads|manages|directs|supervises|works|serves|joins|leaves|appointed|hired|fired|promoted|demoted|graduated|studied|researched|collaborated|partnered|co-authored|co-founded|co-created|co-developed))',
                r'(?:CEO|CTO|CIO|CFO|COO|VP|President|Director|Manager|Lead|Principal|Senior|Junior|Associate|Researcher|Scientist|Engineer|Developer|Designer|Analyst|Consultant|Advisor|Professor|Dr\.|PhD|MD)\s+([A-Z][a-z]+ [A-Z][a-z]+)',
                r'([A-Z][a-z]+ [A-Z][a-z]+)(?:\s(?:et al\.|and colleagues|and team|and researchers|and scientists|and engineers|and developers))'
            ],
            'technologies': [
                r'\b(artificial intelligence|machine learning|deep learning|neural networks|transformer|BERT|GPT|LLM|large language model|natural language processing|NLP|computer vision|CV|reinforcement learning|RL|supervised learning|unsupervised learning|semi-supervised learning|self-supervised learning|transfer learning|meta-learning|few-shot learning|zero-shot learning|multi-task learning|continual learning|federated learning|distributed learning|parallel computing|quantum computing|edge computing|cloud computing|serverless|microservices|containerization|Kubernetes|Docker|blockchain|cryptocurrency|Bitcoin|Ethereum|NFT|DeFi|web3|metaverse|virtual reality|VR|augmented reality|AR|mixed reality|MR|IoT|Internet of Things|5G|6G|WiFi|Bluetooth|GPS|RFID|NFC|API|REST|GraphQL|JSON|XML|HTML|CSS|JavaScript|Python|Java|C\+\+|C#|Go|Rust|Swift|Kotlin|TypeScript|React|Angular|Vue|Node\.js|Django|Flask|Rails|Spring|Laravel|Express|MongoDB|PostgreSQL|MySQL|SQLite|Redis|Elasticsearch|Apache|Nginx|AWS|Azure|GCP|Firebase|Heroku|Vercel|Netlify|GitHub|GitLab|Bitbucket|Jenkins|Travis|CircleCI|Docker|Kubernetes|Terraform|Ansible|Chef|Puppet|Vagrant|VMware|VirtualBox|Linux|Ubuntu|CentOS|RHEL|Windows|macOS|iOS|Android|TensorFlow|PyTorch|Keras|Scikit-learn|Pandas|NumPy|Matplotlib|Seaborn|Jupyter|Colab|Kaggle|Tableau|Power BI|Grafana|Prometheus|ELK Stack|Splunk|New Relic|Datadog|PagerDuty|Slack|Teams|Zoom|Discord|Notion|Figma|Sketch|Photoshop|Illustrator|InDesign|Premiere|After Effects|Blender|Unity|Unreal|Godot|Steam|Epic Games|PlayStation|Xbox|Nintendo|Switch|Oculus|HTC Vive|Magic Leap|HoloLens)\b',
                r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*(?:\s(?:AI|ML|DL|NLP|CV|RL|API|SDK|CLI|GUI|UI|UX|AR|VR|MR|IoT|SaaS|PaaS|IaaS|CRM|ERP|CMS|CDN|DNS|VPN|SSL|TLS|HTTP|HTTPS|FTP|SSH|TCP|UDP|IP|URL|URI|SQL|NoSQL|CRUD|MVC|MVP|MVVM|OOP|ORM|JWT|OAuth|SAML|LDAP|AD|CI\/CD|DevOps|MLOps|DataOps|GitOps|Infrastructure as Code|IaC|Configuration Management|CM|Version Control|VC|Bug Tracking|Project Management|PM|Agile|Scrum|Kanban|Waterfall|Lean|Six Sigma|ITIL|COBIT|SOX|GDPR|HIPAA|PCI|ISO|NIST|OWASP|SANS|CVE|CVSS|MITRE|ATT&CK|Zero Trust|Defense in Depth|Threat Intelligence|TI|Security Information and Event Management|SIEM|Security Orchestration Automation and Response|SOAR|Endpoint Detection and Response|EDR|Extended Detection and Response|XDR|Network Detection and Response|NDR|User and Entity Behavior Analytics|UEBA|Data Loss Prevention|DLP|Identity and Access Management|IAM|Privileged Access Management|PAM|Multi-Factor Authentication|MFA|Single Sign-On|SSO|Public Key Infrastructure|PKI|Certificate Authority|CA|Hardware Security Module|HSM|Trusted Platform Module|TPM|Secure Boot|UEFI|BIOS|Firmware|Microcode|Hypervisor|Virtual Machine|VM|Container|Microservice|Serverless|Function as a Service|FaaS|Backend as a Service|BaaS|Database as a Service|DBaaS|Platform as a Service|PaaS|Infrastructure as a Service|IaaS|Software as a Service|SaaS|Desktop as a Service|DaaS|Network as a Service|NaaS|Storage as a Service|STaaS|Security as a Service|SECaaS|Disaster Recovery as a Service|DRaaS|Backup as a Service|BaaS|Monitoring as a Service|MaaS|Logging as a Service|LaaS|Analytics as a Service|AaaS|Machine Learning as a Service|MLaaS|Artificial Intelligence as a Service|AIaaS)))\b'
            ],
            'research_areas': [
                r'\b(computer science|artificial intelligence|machine learning|data science|software engineering|cybersecurity|information security|network security|cryptography|human-computer interaction|HCI|user experience|UX|user interface|UI|information systems|IS|management information systems|MIS|decision support systems|DSS|business intelligence|BI|data mining|data analytics|big data|data warehousing|database systems|distributed systems|operating systems|computer networks|wireless networks|mobile computing|cloud computing|edge computing|quantum computing|high-performance computing|HPC|parallel computing|grid computing|cluster computing|supercomputing|embedded systems|real-time systems|robotics|automation|control systems|signal processing|image processing|computer vision|computer graphics|computational geometry|computational biology|bioinformatics|computational chemistry|computational physics|computational mathematics|numerical methods|optimization|linear programming|integer programming|dynamic programming|game theory|operations research|OR|industrial engineering|IE|systems engineering|SE|reliability engineering|quality assurance|QA|quality control|QC|statistical quality control|SQC|six sigma|lean manufacturing|total quality management|TQM|business process management|BPM|enterprise resource planning|ERP|customer relationship management|CRM|supply chain management|SCM|logistics|transportation|warehousing|inventory management|procurement|sourcing|vendor management|project management|PM|program management|portfolio management|risk management|financial engineering|quantitative finance|algorithmic trading|high-frequency trading|HFT|financial technology|fintech|blockchain technology|cryptocurrency|digital currency|central bank digital currency|CBDC|decentralized finance|DeFi|non-fungible token|NFT|smart contracts|distributed ledger technology|DLT|peer-to-peer|P2P|consensus algorithms|proof of work|PoW|proof of stake|PoS|delegated proof of stake|DPoS|practical byzantine fault tolerance|pBFT|tendermint|ethereum|bitcoin|litecoin|ripple|cardano|polkadot|chainlink|solana|avalanche|terra|luna|cosmos|stellar|tezos|algorand|hedera|hashgraph|IOTA|nano|monero|zcash|dash|dogecoin|shiba inu|binance coin|BNB|tether|USDT|USD coin|USDC|dai|maker|compound|aave|uniswap|sushiswap|pancakeswap|curve|balancer|synthetix|yearn finance|1inch|0x|kyber network|bancor|loopring|ren|republic protocol|ocean protocol|filecoin|storj|siacoin|arweave|helium|theta|enjin|chiliz|basic attention token|BAT|brave|metamask|trust wallet|coinbase wallet|ledger|trezor|exodus|atomic wallet|myetherwallet|mew|etherscan|bscscan|polygonscan|arbiscan|optimistic etherscan|fantom explorer|avalanche explorer|solana explorer|cardano explorer|polkadot explorer|cosmos explorer|stellar explorer|tezos explorer|algorand explorer|hedera explorer|IOTA explorer|nano explorer|monero explorer|zcash explorer|dash explorer|dogecoin explorer|bitcoin explorer|litecoin explorer|ripple explorer)\b'
            ],
            'venues': [
                r'\b(?:Conference|Symposium|Workshop|Journal|Proceedings|Transactions|Letters|Magazine|Review|Annals|Bulletin|Gazette|Quarterly|Annual|International|National|Regional|Local|Global|Worldwide|Universal|General|Special|Advanced|Modern|Contemporary|Current|Recent|Latest|New|Novel|Innovative|Creative|Original|Unique|Pioneering|Groundbreaking|Revolutionary|Transformative|Disruptive|Emerging|Trending|Popular|Leading|Top|Premier|Elite|Prestigious|Distinguished|Renowned|Famous|Well-known|Established|Traditional|Classic|Standard|Conventional|Mainstream|Alternative|Independent|Open|Free|Public|Private|Commercial|Academic|Scientific|Technical|Professional|Industrial|Corporate|Government|Military|Defense|Healthcare|Medical|Clinical|Biomedical|Pharmaceutical|Educational|Training|Research|Development|Innovation|Technology|Engineering|Science|Mathematics|Statistics|Physics|Chemistry|Biology|Medicine|Psychology|Sociology|Anthropology|Economics|Finance|Business|Management|Marketing|Sales|Operations|Logistics|Supply Chain|Human Resources|HR|Information Technology|IT|Computer Science|CS|Software Engineering|SE|Data Science|DS|Artificial Intelligence|AI|Machine Learning|ML|Deep Learning|DL|Natural Language Processing|NLP|Computer Vision|CV|Robotics|Automation|Control|Signal Processing|Image Processing|Graphics|Visualization|User Interface|UI|User Experience|UX|Human-Computer Interaction|HCI|Cybersecurity|Information Security|Network Security|Cryptography|Blockchain|Cryptocurrency|Quantum Computing|Cloud Computing|Edge Computing|Internet of Things|IoT|5G|6G|Wireless|Mobile|Telecommunications|Networking|Distributed Systems|Parallel Computing|High-Performance Computing|HPC|Supercomputing|Grid Computing|Cluster Computing|Embedded Systems|Real-Time Systems|Operating Systems|Database Systems|Data Mining|Big Data|Analytics|Business Intelligence|BI|Decision Support|Knowledge Management|Information Systems|IS|Management Information Systems|MIS|Enterprise Resource Planning|ERP|Customer Relationship Management|CRM|Supply Chain Management|SCM|Project Management|PM|Quality Assurance|QA|Quality Control|QC|Risk Management|Compliance|Governance|Audit|Accounting|Finance|Investment|Banking|Insurance|Real Estate|Construction|Manufacturing|Production|Operations|Logistics|Transportation|Energy|Environment|Sustainability|Climate|Weather|Agriculture|Food|Nutrition|Health|Fitness|Sports|Recreation|Entertainment|Media|Broadcasting|Publishing|Journalism|Communications|Public Relations|PR|Advertising|Marketing|Sales|Retail|E-commerce|Digital Marketing|Social Media|Content|Creative|Design|Art|Fashion|Beauty|Travel|Tourism|Hospitality|Hotels|Restaurants|Food Service|Event Management|Wedding Planning|Party Planning|Catering|Photography|Videography|Music|Audio|Video|Film|Television|TV|Radio|Podcast|Streaming|Gaming|Esports|Virtual Reality|VR|Augmented Reality|AR|Mixed Reality|MR|Metaverse|Web3|NFT|DeFi|Crypto|Digital Assets|Digital Transformation|Digital Innovation|Digital Strategy|Digital Marketing|Digital Commerce|Digital Payments|Digital Banking|Digital Health|Digital Education|Digital Government|Digital Society|Digital Economy|Digital Culture|Digital Art|Digital Music|Digital Media|Digital Content|Digital Publishing|Digital Broadcasting|Digital Communications|Digital Advertising|Digital Analytics|Digital Security|Digital Privacy|Digital Rights|Digital Ethics|Digital Law|Digital Policy|Digital Regulation|Digital Standards|Digital Infrastructure|Digital Platforms|Digital Ecosystems|Digital Networks|Digital Communities|Digital Collaboration|Digital Workspace|Digital Tools|Digital Solutions|Digital Services|Digital Products|Digital Experiences|Digital Journeys|Digital Touchpoints|Digital Channels|Digital Interactions|Digital Engagement|Digital Relationships|Digital Trust|Digital Reputation|Digital Brand|Digital Identity|Digital Persona|Digital Avatar|Digital Twin|Digital Mirror|Digital Shadow|Digital Footprint|Digital Trail|Digital Legacy|Digital Heritage|Digital Archive|Digital Library|Digital Museum|Digital Gallery|Digital Exhibition|Digital Collection|Digital Catalog|Digital Inventory|Digital Asset Management|DAM|Digital Rights Management|DRM|Digital Content Management|DCM|Digital Document Management|DDM|Digital Workflow|Digital Process|Digital Automation|Digital Transformation|Digital Innovation|Digital Disruption|Digital Revolution|Digital Evolution|Digital Maturity|Digital Readiness|Digital Adoption|Digital Literacy|Digital Skills|Digital Competency|Digital Fluency|Digital Natives|Digital Immigrants|Digital Divide|Digital Inclusion|Digital Exclusion|Digital Accessibility|Digital Usability|Digital Design|Digital Interface|Digital Architecture|Digital Infrastructure|Digital Foundation|Digital Framework|Digital Model|Digital Structure|Digital System|Digital Platform|Digital Environment|Digital Ecosystem|Digital Landscape|Digital Terrain|Digital Space|Digital Realm|Digital World|Digital Universe|Digital Reality|Digital Dimension|Digital Layer|Digital Level|Digital Stage|Digital Scene|Digital Setting|Digital Context|Digital Situation|Digital Scenario|Digital Case|Digital Example|Digital Instance|Digital Sample|Digital Specimen|Digital Prototype|Digital Demo|Digital Proof|Digital Concept|Digital Experiment|Digital Test|Digital Trial|Digital Study|Digital Research|Digital Investigation|Digital Exploration|Digital Discovery|Digital Finding|Digital Result|Digital Outcome|Digital Conclusion|Digital Recommendation|Digital Suggestion|Digital Proposal|Digital Plan|Digital Strategy|Digital Roadmap|Digital Vision|Digital Mission|Digital Goal|Digital Objective|Digital Target|Digital Metric|Digital KPI|Digital ROI|Digital Value|Digital Benefit|Digital Advantage|Digital Opportunity|Digital Challenge|Digital Problem|Digital Issue|Digital Risk|Digital Threat|Digital Vulnerability|Digital Attack|Digital Breach|Digital Incident|Digital Crisis|Digital Emergency|Digital Disaster|Digital Recovery|Digital Backup|Digital Restore|Digital Sync|Digital Update|Digital Upgrade|Digital Migration|Digital Transition|Digital Change|Digital Shift|Digital Move|Digital Transfer|Digital Exchange|Digital Trade|Digital Deal|Digital Transaction|Digital Payment|Digital Money|Digital Currency|Digital Coin|Digital Token|Digital Wallet|Digital Bank|Digital Account|Digital Balance|Digital Statement|Digital Receipt|Digital Invoice|Digital Bill|Digital Contract|Digital Agreement|Digital License|Digital Permit|Digital Certificate|Digital Credential|Digital Badge|Digital Award|Digital Recognition|Digital Achievement|Digital Success|Digital Victory|Digital Win|Digital Triumph|Digital Accomplishment|Digital Milestone|Digital Progress|Digital Development|Digital Growth|Digital Expansion|Digital Scale|Digital Size|Digital Volume|Digital Capacity|Digital Capability|Digital Performance|Digital Speed|Digital Efficiency|Digital Productivity|Digital Quality|Digital Reliability|Digital Stability|Digital Consistency|Digital Accuracy|Digital Precision|Digital Excellence|Digital Perfection|Digital Optimization|Digital Enhancement|Digital Improvement|Digital Refinement|Digital Polish|Digital Finish|Digital Completion|Digital Delivery|Digital Launch|Digital Release|Digital Deployment|Digital Implementation|Digital Execution|Digital Operation|Digital Management|Digital Administration|Digital Governance|Digital Leadership|Digital Direction|Digital Guidance|Digital Support|Digital Assistance|Digital Help|Digital Service|Digital Care|Digital Maintenance|Digital Monitoring|Digital Tracking|Digital Analysis|Digital Evaluation|Digital Assessment|Digital Review|Digital Audit|Digital Inspection|Digital Examination|Digital Check|Digital Verification|Digital Validation|Digital Confirmation|Digital Approval|Digital Authorization|Digital Permission|Digital Access|Digital Entry|Digital Login|Digital Authentication|Digital Security|Digital Protection|Digital Safety|Digital Privacy|Digital Confidentiality|Digital Anonymity|Digital Transparency|Digital Openness|Digital Visibility|Digital Clarity|Digital Understanding|Digital Knowledge|Digital Wisdom|Digital Intelligence|Digital Insight|Digital Awareness|Digital Consciousness|Digital Mindfulness|Digital Attention|Digital Focus|Digital Concentration|Digital Dedication|Digital Commitment|Digital Passion|Digital Enthusiasm|Digital Energy|Digital Power|Digital Strength|Digital Force|Digital Impact|Digital Influence|Digital Effect|Digital Change|Digital Transformation|Digital Revolution|Digital Evolution|Digital Progress|Digital Advancement|Digital Development|Digital Growth|Digital Expansion|Digital Innovation|Digital Creativity|Digital Imagination|Digital Vision|Digital Dream|Digital Aspiration|Digital Hope|Digital Faith|Digital Belief|Digital Trust|Digital Confidence|Digital Courage|Digital Bravery|Digital Boldness|Digital Determination|Digital Persistence|Digital Perseverance|Digital Resilience|Digital Endurance|Digital Stamina|Digital Vitality|Digital Health|Digital Wellness|Digital Fitness|Digital Balance|Digital Harmony|Digital Peace|Digital Calm|Digital Serenity|Digital Tranquility|Digital Quiet|Digital Silence|Digital Stillness|Digital Rest|Digital Relaxation|Digital Comfort|Digital Ease|Digital Simplicity|Digital Clarity|Digital Purity|Digital Cleanliness|Digital Order|Digital Organization|Digital Structure|Digital System|Digital Method|Digital Process|Digital Procedure|Digital Protocol|Digital Standard|Digital Rule|Digital Law|Digital Regulation|Digital Policy|Digital Guideline|Digital Principle|Digital Value|Digital Ethic|Digital Moral|Digital Right|Digital Wrong|Digital Good|Digital Bad|Digital Positive|Digital Negative|Digital Light|Digital Dark|Digital Bright|Digital Dim|Digital Clear|Digital Unclear|Digital Sharp|Digital Blurry|Digital Focused|Digital Unfocused|Digital Centered|Digital Balanced|Digital Stable|Digital Unstable|Digital Steady|Digital Unsteady|Digital Consistent|Digital Inconsistent|Digital Reliable|Digital Unreliable|Digital Dependable|Digital Undependable|Digital Trustworthy|Digital Untrustworthy|Digital Honest|Digital Dishonest|Digital True|Digital False|Digital Real|Digital Fake|Digital Genuine|Digital Artificial|Digital Natural|Digital Synthetic|Digital Organic|Digital Mechanical|Digital Manual|Digital Automatic|Digital Smart|Digital Intelligent|Digital Wise|Digital Foolish|Digital Clever|Digital Stupid|Digital Quick|Digital Slow|Digital Fast|Digital Sluggish|Digital Efficient|Digital Inefficient|Digital Effective|Digital Ineffective|Digital Productive|Digital Unproductive|Digital Useful|Digital Useless|Digital Valuable|Digital Worthless|Digital Important|Digital Unimportant|Digital Significant|Digital Insignificant|Digital Relevant|Digital Irrelevant|Digital Meaningful|Digital Meaningless|Digital Purposeful|Digital Purposeless|Digital Intentional|Digital Unintentional|Digital Deliberate|Digital Accidental|Digital Planned|Digital Unplanned|Digital Organized|Digital Disorganized|Digital Structured|Digital Unstructured|Digital Systematic|Digital Unsystematic|Digital Methodical|Digital Unmethodical|Digital Orderly|Digital Disorderly|Digital Neat|Digital Messy|Digital Clean|Digital Dirty|Digital Pure|Digital Impure|Digital Fresh|Digital Stale|Digital New|Digital Old|Digital Modern|Digital Ancient|Digital Contemporary|Digital Traditional|Digital Current|Digital Outdated|Digital Updated|Digital Obsolete|Digital Advanced|Digital Primitive|Digital Sophisticated|Digital Simple|Digital Complex|Digital Complicated|Digital Easy|Digital Difficult|Digital Hard|Digital Soft|Digital Tough|Digital Gentle|Digital Rough|Digital Smooth|Digital Bumpy|Digital Flat|Digital Curved|Digital Straight|Digital Crooked|Digital Perfect|Digital Imperfect|Digital Complete|Digital Incomplete|Digital Whole|Digital Partial|Digital Full|Digital Empty|Digital Filled|Digital Vacant|Digital Occupied|Digital Available|Digital Unavailable|Digital Accessible|Digital Inaccessible|Digital Open|Digital Closed|Digital Public|Digital Private|Digital Personal|Digital Professional|Digital Business|Digital Commercial|Digital Industrial|Digital Academic|Digital Educational|Digital Scientific|Digital Technical|Digital Medical|Digital Legal|Digital Financial|Digital Economic|Digital Political|Digital Social|Digital Cultural|Digital Religious|Digital Spiritual|Digital Philosophical|Digital Psychological|Digital Physical|Digital Mental|Digital Emotional|Digital Intellectual|Digital Creative|Digital Artistic|Digital Musical|Digital Literary|Digital Poetic|Digital Dramatic|Digital Comic|Digital Tragic|Digital Romantic|Digital Realistic|Digital Fantastic|Digital Magical|Digital Mystical|Digital Mysterious|Digital Secret|Digital Hidden|Digital Visible|Digital Obvious|Digital Clear|Digital Apparent|Digital Evident|Digital Manifest|Digital Explicit|Digital Implicit|Digital Direct|Digital Indirect|Digital Straight|Digital Circular|Digital Linear|Digital Nonlinear|Digital Parallel|Digital Perpendicular|Digital Horizontal|Digital Vertical|Digital Diagonal|Digital Angular|Digital Rounded|Digital Squared|Digital Triangular|Digital Circular|Digital Oval|Digital Rectangular|Digital Polygonal|Digital Geometric|Digital Organic|Digital Abstract|Digital Concrete|Digital Tangible|Digital Intangible|Digital Material|Digital Immaterial|Digital Physical|Digital Virtual|Digital Real|Digital Imaginary|Digital Actual|Digital Theoretical|Digital Practical|Digital Applied|Digital Pure|Digital Mixed|Digital Hybrid|Digital Composite|Digital Integrated|Digital Unified|Digital Combined|Digital Merged|Digital Blended|Digital Fused|Digital Connected|Digital Disconnected|Digital Linked|Digital Unlinked|Digital Joined|Digital Separated|Digital United|Digital Divided|Digital Together|Digital Apart|Digital Close|Digital Far|Digital Near|Digital Distant|Digital Local|Digital Remote|Digital Central|Digital Peripheral|Digital Core|Digital Edge|Digital Inside|Digital Outside|Digital Internal|Digital External|Digital Inner|Digital Outer|Digital Deep|Digital Shallow|Digital High|Digital Low|Digital Up|Digital Down|Digital Above|Digital Below|Digital Over|Digital Under|Digital Front|Digital Back|Digital Forward|Digital Backward|Digital Ahead|Digital Behind|Digital Left|Digital Right|Digital Side|Digital Center|Digital Middle|Digital Beginning|Digital End|Digital Start|Digital Finish|Digital First|Digital Last|Digital Early|Digital Late|Digital Soon|Digital Later|Digital Now|Digital Then|Digital Here|Digital There|Digital This|Digital That|Digital These|Digital Those|Digital All|Digital None|Digital Some|Digital Many|Digital Few|Digital More|Digital Less|Digital Most|Digital Least|Digital Best|Digital Worst|Digital Better|Digital Worse|Digital Good|Digital Bad|Digital Great|Digital Terrible|Digital Excellent|Digital Poor|Digital Outstanding|Digital Mediocre|Digital Superior|Digital Inferior|Digital Premium|Digital Standard|Digital Basic|Digital Advanced|Digital Elementary|Digital Fundamental|Digital Essential|Digital Optional|Digital Required|Digital Necessary|Digital Sufficient|Digital Insufficient|Digital Adequate|Digital Inadequate|Digital Appropriate|Digital Inappropriate|Digital Suitable|Digital Unsuitable|Digital Proper|Digital Improper|Digital Correct|Digital Incorrect|Digital Right|Digital Wrong|Digital Accurate|Digital Inaccurate|Digital Precise|Digital Imprecise|Digital Exact|Digital Approximate|Digital Specific|Digital General|Digital Particular|Digital Universal|Digital Individual|Digital Collective|Digital Personal|Digital Shared|Digital Common|Digital Rare|Digital Unique|Digital Typical|Digital Unusual|Digital Normal|Digital Abnormal|Digital Regular|Digital Irregular|Digital Standard|Digital Nonstandard|Digital Ordinary|Digital Extraordinary|Digital Special|Digital Regular|Digital Custom|Digital Default|Digital Optional|Digital Mandatory|Digital Voluntary|Digital Forced|Digital Free|Digital Paid|Digital Premium|Digital Basic|Digital Standard|Digital Advanced|Digital Professional|Digital Enterprise|Digital Business|Digital Commercial|Digital Industrial|Digital Academic|Digital Educational|Digital Scientific|Digital Research|Digital Development|Digital Innovation|Digital Technology|Digital Engineering|Digital Science|Digital Mathematics|Digital Statistics|Digital Physics|Digital Chemistry|Digital Biology|Digital Medicine|Digital Health|Digital Psychology|Digital Sociology|Digital Anthropology|Digital Economics|Digital Finance|Digital Business|Digital Management|Digital Marketing|Digital Sales|Digital Operations|Digital Logistics|Digital Human Resources|HR|Information Technology|IT|Computer Science|CS|Software Engineering|SE|Data Science|DS|Artificial Intelligence|AI|Machine Learning|ML|Deep Learning|DL|Natural Language Processing|NLP|Computer Vision|CV|Robotics|Automation|Control|Signal Processing|Image Processing|Graphics|Visualization|User Interface|UI|User Experience|UX|Human-Computer Interaction|HCI|Cybersecurity|Information Security|Network Security|Cryptography|Blockchain|Cryptocurrency|Quantum Computing|Cloud Computing|Edge Computing|Internet of Things|IoT)\s+(?:on|in|of|for)\s+[A-Z][a-zA-Z\s]+)\b'
            ]
        }
    
    def _load_relationship_patterns(self) -> Dict:
        """Load patterns for relationship extraction"""
        return {
            'collaboration': [
                r'([A-Z][a-zA-Z\s]+)\s+(?:collaborat|partner|work|team|join)\w*\s+(?:with|together)\s+([A-Z][a-zA-Z\s]+)',
                r'([A-Z][a-zA-Z\s]+)\s+(?:and|&)\s+([A-Z][a-zA-Z\s]+)\s+(?:collaborat|partner|work|develop|creat)\w*',
                r'(?:joint|shared|collective)\s+(?:project|research|development|effort|initiative|venture)\s+(?:between|among|by)\s+([A-Z][a-zA-Z\s]+)\s+(?:and|&|,)\s+([A-Z][a-zA-Z\s]+)'
            ],
            'competition': [
                r'([A-Z][a-zA-Z\s]+)\s+(?:compet|rival|challeng|vs|versus|against)\w*\s+([A-Z][a-zA-Z\s]+)',
                r'([A-Z][a-zA-Z\s]+)\s+(?:and|&)\s+([A-Z][a-zA-Z\s]+)\s+(?:compet|rival|fight|battle)\w*',
                r'(?:competition|rivalry|battle|fight)\s+(?:between|among)\s+([A-Z][a-zA-Z\s]+)\s+(?:and|&|,)\s+([A-Z][a-zA-Z\s]+)'
            ],
            'investment': [
                r'([A-Z][a-zA-Z\s]+)\s+(?:invest|fund|financ|back|support)\w*\s+([A-Z][a-zA-Z\s]+)',
                r'([A-Z][a-zA-Z\s]+)\s+(?:receiv|rais|secur)\w*\s+(?:investment|funding|capital)\s+(?:from|by)\s+([A-Z][a-zA-Z\s]+)',
                r'([A-Z][a-zA-Z\s]+)\s+(?:led|participate)\w*\s+(?:in\s+)?(?:funding|investment|round)\s+(?:for|of)\s+([A-Z][a-zA-Z\s]+)'
            ],
            'acquisition': [
                r'([A-Z][a-zA-Z\s]+)\s+(?:acquir|purchas|buy|take\s+over)\w*\s+([A-Z][a-zA-Z\s]+)',
                r'([A-Z][a-zA-Z\s]+)\s+(?:was|has\s+been|got)\s+(?:acquired|purchased|bought)\s+(?:by|from)\s+([A-Z][a-zA-Z\s]+)',
                r'(?:acquisition|purchase|buyout|takeover)\s+(?:of|by)\s+([A-Z][a-zA-Z\s]+)\s+(?:by|from)\s+([A-Z][a-zA-Z\s]+)'
            ],
            'authorship': [
                r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s+(?:authored|wrote|published|co-authored)\s+([A-Z][a-zA-Z\s:]+)',
                r'([A-Z][a-zA-Z\s:]+)\s+(?:by|authored by|written by)\s+([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)*)',
                r'(?:Authors?|Writers?|Co-authors?):\s*([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)*(?:,\s*[A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)*)*)'
            ],
            'employment': [
                r'([A-Z][a-z]+ [A-Z][a-z]+)\s+(?:works?|worked|employed|hired)\s+(?:at|for|by)\s+([A-Z][a-zA-Z\s]+)',
                r'([A-Z][a-zA-Z\s]+)\s+(?:hired|employed|recruits?|appointed)\s+([A-Z][a-z]+ [A-Z][a-z]+)',
                r'([A-Z][a-z]+ [A-Z][a-z]+),?\s+(?:CEO|CTO|CIO|CFO|COO|VP|President|Director|Manager)\s+(?:at|of)\s+([A-Z][a-zA-Z\s]+)'
            ],
            'citation': [
                r'([A-Z][a-zA-Z\s:]+)\s+(?:cites?|references?|builds?\s+on|extends?)\s+([A-Z][a-zA-Z\s:]+)',
                r'(?:building on|extending|based on|inspired by)\s+([A-Z][a-zA-Z\s:]+),?\s+([A-Z][a-zA-Z\s:]+)',
                r'([A-Z][a-zA-Z\s:]+)\s+(?:was|has been)\s+(?:cited|referenced)\s+(?:by|in)\s+([A-Z][a-zA-Z\s:]+)'
            ],
            'technology_usage': [
                r'([A-Z][a-zA-Z\s]+)\s+(?:uses?|utilizes?|employs?|implements?|adopts?)\s+([A-Z][a-zA-Z\s]+)',
                r'([A-Z][a-zA-Z\s]+)\s+(?:is|was)\s+(?:built|developed|created)\s+(?:using|with|on)\s+([A-Z][a-zA-Z\s]+)',
                r'(?:using|with|on|based on)\s+([A-Z][a-zA-Z\s]+),?\s+([A-Z][a-zA-Z\s]+)\s+(?:was|is)\s+(?:built|developed|created)'
            ]
        }
    
    def extract_entities_and_relationships(self, documents: List[Dict]) -> Dict:
        """Extract entities and relationships from documents"""
        logger.info(f"Extracting entities and relationships from {len(documents)} documents...")
        
        extracted_data = {
            'entities': {
                'companies': set(),
                'people': set(),
                'technologies': set(),
                'research_areas': set(),
                'venues': set(),
                'papers': set()
            },
            'relationships': []
        }
        
        for doc_idx, doc in enumerate(documents):
            content = f"{doc.get('title', '')} {doc.get('content', '')}"
            
            # Extract entities
            doc_entities = self._extract_entities_from_text(content)
            
            # Merge entities
            for entity_type, entities in doc_entities.items():
                extracted_data['entities'][entity_type].update(entities)
            
            # Extract relationships
            doc_relationships = self._extract_relationships_from_text(content, doc)
            extracted_data['relationships'].extend(doc_relationships)
            
            # Add paper as entity if it's a research paper
            if doc.get('document_type') in ['research_paper', 'arxiv_paper']:
                title = doc.get('title', '').strip()
                if title:
                    extracted_data['entities']['papers'].add(title)
            
            if (doc_idx + 1) % 100 == 0:
                logger.info(f"Processed {doc_idx + 1}/{len(documents)} documents...")
        
        # Convert sets to lists for JSON serialization
        for entity_type in extracted_data['entities']:
            extracted_data['entities'][entity_type] = list(extracted_data['entities'][entity_type])
        
        # Log statistics
        total_entities = sum(len(entities) for entities in extracted_data['entities'].values())
        logger.info(f"Extracted {total_entities} entities and {len(extracted_data['relationships'])} relationships")
        
        for entity_type, entities in extracted_data['entities'].items():
            logger.info(f"  {entity_type}: {len(entities)}")
        
        return extracted_data
    
    def _extract_entities_from_text(self, text: str) -> Dict[str, Set[str]]:
        """Extract entities from a single text"""
        entities = {
            'companies': set(),
            'people': set(),
            'technologies': set(),
            'research_areas': set(),
            'venues': set()
        }
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    entity = match.group(1) if match.groups() else match.group(0)
                    entity = entity.strip()
                    
                    # Filter out noise
                    if self._is_valid_entity(entity, entity_type):
                        entities[entity_type].add(entity)
        
        return entities
    
    def _extract_relationships_from_text(self, text: str, doc: Dict) -> List[Dict]:
        """Extract relationships from a single text"""
        relationships = []
        
        for rel_type, patterns in self.relationship_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        entity1 = match.group(1).strip()
                        entity2 = match.group(2).strip()
                        
                        if self._is_valid_relationship(entity1, entity2, rel_type):
                            relationship = {
                                'type': rel_type,
                                'entity1': entity1,
                                'entity2': entity2,
                                'source_document': doc.get('title', ''),
                                'source_type': doc.get('document_type', ''),
                                'confidence': self._calculate_confidence(match.group(0), rel_type)
                            }
                            relationships.append(relationship)
        
        return relationships
    
    def _is_valid_entity(self, entity: str, entity_type: str) -> bool:
        """Validate extracted entity"""
        if not entity or len(entity) < 2 or len(entity) > 100:
            return False
        
        # Check for common noise patterns
        noise_patterns = [
            r'^[a-z]+$',  # All lowercase
            r'^\d+$',     # All digits
            r'^[^a-zA-Z]*$',  # No letters
            r'^\s*$',     # Only whitespace
            r'^(the|and|or|but|for|at|in|on|with|by|from|to|of|a|an)$'  # Stop words
        ]
        
        for pattern in noise_patterns:
            if re.match(pattern, entity, re.IGNORECASE):
                return False
        
        # Type-specific validation
        if entity_type == 'people':
            # Should have at least first and last name
            parts = entity.split()
            if len(parts) < 2:
                return False
            # Check for title-like patterns
            if any(part.lower() in ['dr', 'prof', 'mr', 'ms', 'mrs'] for part in parts):
                return True
        
        elif entity_type == 'companies':
            # Should be capitalized
            if not entity[0].isupper():
                return False
        
        return True
    
    def _is_valid_relationship(self, entity1: str, entity2: str, rel_type: str) -> bool:
        """Validate extracted relationship"""
        if not entity1 or not entity2 or entity1 == entity2:
            return False
        
        if len(entity1) < 2 or len(entity2) < 2:
            return False
        
        if len(entity1) > 100 or len(entity2) > 100:
            return False
        
        return True
    
    def _calculate_confidence(self, match_text: str, rel_type: str) -> float:
        """Calculate confidence score for relationship"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for certain patterns
        if rel_type == 'collaboration':
            if any(word in match_text.lower() for word in ['partnership', 'joint', 'together']):
                confidence += 0.2
        
        elif rel_type == 'investment':
            if any(word in match_text.lower() for word in ['million', 'billion', 'funding', 'series']):
                confidence += 0.3
        
        elif rel_type == 'acquisition':
            if any(word in match_text.lower() for word in ['acquired', 'purchased', 'bought']):
                confidence += 0.3
        
        return min(confidence, 1.0)
    
    def build_enhanced_knowledge_graph(self, extracted_data: Dict) -> Dict:
        """Build enhanced knowledge graph in Neo4j"""
        logger.info("Building enhanced knowledge graph...")
        
        try:
            with db.driver.session() as session:
                stats = {
                    'nodes_created': 0,
                    'relationships_created': 0,
                    'entities_by_type': {}
                }
                
                # Create entity nodes
                for entity_type, entities in extracted_data['entities'].items():
                    created_count = 0
                    
                    if entity_type == 'companies':
                        for company in entities:
                            session.run("""
                                MERGE (c:Company {name: $name})
                                ON CREATE SET c.source = 'enhanced_extraction', 
                                             c.created_date = datetime(),
                                             c.entity_type = 'company'
                            """, name=company)
                            created_count += 1
                    
                    elif entity_type == 'people':
                        for person in entities:
                            session.run("""
                                MERGE (p:Person {name: $name})
                                ON CREATE SET p.source = 'enhanced_extraction', 
                                             p.created_date = datetime(),
                                             p.entity_type = 'person'
                            """, name=person)
                            created_count += 1
                    
                    elif entity_type == 'technologies':
                        for tech in entities:
                            session.run("""
                                MERGE (t:Technology {name: $name})
                                ON CREATE SET t.source = 'enhanced_extraction', 
                                             t.created_date = datetime(),
                                             t.entity_type = 'technology'
                            """, name=tech)
                            created_count += 1
                    
                    elif entity_type == 'research_areas':
                        for area in entities:
                            session.run("""
                                MERGE (r:Topic {name: $name})
                                ON CREATE SET r.description = $description,
                                             r.source = 'enhanced_extraction', 
                                             r.created_date = datetime(),
                                             r.entity_type = 'research_area'
                            """, name=area, description=f"Research area: {area}")
                            created_count += 1
                    
                    elif entity_type == 'venues':
                        for venue in entities:
                            session.run("""
                                MERGE (v:Venue {name: $name})
                                ON CREATE SET v.source = 'enhanced_extraction', 
                                             v.created_date = datetime(),
                                             v.entity_type = 'venue'
                            """, name=venue)
                            created_count += 1
                    
                    elif entity_type == 'papers':
                        for paper in entities:
                            session.run("""
                                MERGE (p:Document {title: $title})
                                ON CREATE SET p.source = 'enhanced_extraction', 
                                             p.created_date = datetime(),
                                             p.entity_type = 'paper',
                                             p.document_type = 'research_paper'
                            """, title=paper)
                            created_count += 1
                    
                    stats['entities_by_type'][entity_type] = created_count
                    stats['nodes_created'] += created_count
                
                # Create relationships
                relationship_counts = defaultdict(int)
                
                for rel in extracted_data['relationships']:
                    rel_type = rel['type']
                    entity1 = rel['entity1']
                    entity2 = rel['entity2']
                    confidence = rel.get('confidence', 0.5)
                    
                    if rel_type == 'collaboration':
                        session.run("""
                            MATCH (e1), (e2)
                            WHERE e1.name = $entity1 AND e2.name = $entity2
                            MERGE (e1)-[r:COLLABORATES_WITH]->(e2)
                            ON CREATE SET r.source = 'enhanced_extraction',
                                         r.confidence = $confidence,
                                         r.created_date = datetime()
                        """, entity1=entity1, entity2=entity2, confidence=confidence)
                    
                    elif rel_type == 'competition':
                        session.run("""
                            MATCH (e1), (e2)
                            WHERE e1.name = $entity1 AND e2.name = $entity2
                            MERGE (e1)-[r:COMPETES_WITH]->(e2)
                            ON CREATE SET r.source = 'enhanced_extraction',
                                         r.confidence = $confidence,
                                         r.created_date = datetime()
                        """, entity1=entity1, entity2=entity2, confidence=confidence)
                    
                    elif rel_type == 'investment':
                        session.run("""
                            MATCH (e1), (e2)
                            WHERE e1.name = $entity1 AND e2.name = $entity2
                            MERGE (e1)-[r:INVESTS_IN]->(e2)
                            ON CREATE SET r.source = 'enhanced_extraction',
                                         r.confidence = $confidence,
                                         r.created_date = datetime()
                        """, entity1=entity1, entity2=entity2, confidence=confidence)
                    
                    elif rel_type == 'acquisition':
                        session.run("""
                            MATCH (e1), (e2)
                            WHERE e1.name = $entity1 AND e2.name = $entity2
                            MERGE (e1)-[r:ACQUIRED]->(e2)
                            ON CREATE SET r.source = 'enhanced_extraction',
                                         r.confidence = $confidence,
                                         r.created_date = datetime()
                        """, entity1=entity1, entity2=entity2, confidence=confidence)
                    
                    elif rel_type == 'authorship':
                        session.run("""
                            MATCH (p:Person), (d:Document)
                            WHERE p.name = $entity1 AND d.title = $entity2
                            MERGE (p)-[r:AUTHORED]->(d)
                            ON CREATE SET r.source = 'enhanced_extraction',
                                         r.confidence = $confidence,
                                         r.created_date = datetime()
                        """, entity1=entity1, entity2=entity2, confidence=confidence)
                    
                    elif rel_type == 'employment':
                        session.run("""
                            MATCH (p:Person), (c:Company)
                            WHERE p.name = $entity1 AND c.name = $entity2
                            MERGE (p)-[r:WORKS_AT]->(c)
                            ON CREATE SET r.source = 'enhanced_extraction',
                                         r.confidence = $confidence,
                                         r.created_date = datetime()
                        """, entity1=entity1, entity2=entity2, confidence=confidence)
                    
                    elif rel_type == 'technology_usage':
                        session.run("""
                            MATCH (e1), (t:Technology)
                            WHERE e1.name = $entity1 AND t.name = $entity2
                            MERGE (e1)-[r:USES_TECHNOLOGY]->(t)
                            ON CREATE SET r.source = 'enhanced_extraction',
                                         r.confidence = $confidence,
                                         r.created_date = datetime()
                        """, entity1=entity1, entity2=entity2, confidence=confidence)
                    
                    relationship_counts[rel_type] += 1
                    stats['relationships_created'] += 1
                
                logger.info(f"Enhanced knowledge graph created:")
                logger.info(f"  Nodes created: {stats['nodes_created']}")
                logger.info(f"  Relationships created: {stats['relationships_created']}")
                
                for entity_type, count in stats['entities_by_type'].items():
                    logger.info(f"    {entity_type}: {count}")
                
                for rel_type, count in relationship_counts.items():
                    logger.info(f"    {rel_type}: {count}")
                
                return {
                    'success': True,
                    'stats': stats,
                    'relationship_counts': dict(relationship_counts)
                }
                
        except Exception as e:
            error_msg = f"Error building enhanced knowledge graph: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

def enhance_knowledge_graph_from_documents(documents: List[Dict]) -> Dict:
    """Main function to enhance knowledge graph from collected documents"""
    enhancer = KnowledgeGraphEnhancer()
    
    # Extract entities and relationships
    extracted_data = enhancer.extract_entities_and_relationships(documents)
    
    # Build enhanced knowledge graph
    result = enhancer.build_enhanced_knowledge_graph(extracted_data)
    
    # Add extraction statistics to result
    if result['success']:
        result['extraction_stats'] = {
            'total_entities': sum(len(entities) for entities in extracted_data['entities'].values()),
            'entities_by_type': {k: len(v) for k, v in extracted_data['entities'].items()},
            'total_relationships': len(extracted_data['relationships'])
        }
    
    return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test with sample documents
    sample_docs = [
        {
            'title': 'Google Research Paper on Transformers',
            'content': 'Google and OpenAI collaborate on transformer research. Sundar Pichai announced partnership.',
            'document_type': 'research_paper'
        }
    ]
    
    result = enhance_knowledge_graph_from_documents(sample_docs)
    print(f"Enhancement result: {result}")