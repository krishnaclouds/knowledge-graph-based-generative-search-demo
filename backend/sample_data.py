from dotenv import load_dotenv
load_dotenv()

from database import db
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_database():
    """Clear all existing data"""
    try:
        with db.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        logger.info("Database cleared successfully")
    except Exception as e:
        logger.error(f"Failed to clear database: {e}")
        raise

def create_sample_data():
    """Create comprehensive sample data for testing"""
    try:
        with db.driver.session() as session:
            # Create companies with rich content
            companies_data = [
                {
                    "name": "Google",
                    "industry": "Technology",
                    "founded": 1998,
                    "headquarters": "Mountain View, California",
                    "employees": 182000,
                    "revenue": "282.8 billion USD",
                    "description": "Google LLC is an American multinational technology company focusing on search engine technology, online advertising, cloud computing, computer software, quantum computing, e-commerce, artificial intelligence, and consumer electronics. It has been referred to as 'the most powerful company in the world' and one of the world's most valuable brands due to its market dominance, data collection, and technological advantages in the area of artificial intelligence. Google's parent company Alphabet Inc. is considered one of the Big Five American information technology companies, alongside Amazon, Apple, Meta, and Microsoft. Google was founded on September 4, 1998, by American computer scientists Larry Page and Sergey Brin while they were PhD students at Stanford University in California. Together they own about 14% of its publicly-listed shares and control 56% of its stockholder voting power through super-voting stock. The company went public via an initial public offering (IPO) in 2004. In 2015, Google was reorganized as a wholly-owned subsidiary of Alphabet Inc. Google is Alphabet's largest subsidiary and is a holding company for Alphabet's Internet properties and interests.",
                    "key_products": ["Search", "YouTube", "Android", "Chrome", "Google Cloud", "Gmail", "Google Maps"],
                    "stock_symbol": "GOOGL"
                },
                {
                    "name": "Apple",
                    "industry": "Technology",
                    "founded": 1976,
                    "headquarters": "Cupertino, California",
                    "employees": 164000,
                    "revenue": "394.3 billion USD",
                    "description": "Apple Inc. is an American multinational technology company headquartered in Cupertino, California, that designs, develops, and sells consumer electronics, computer software, and online services. It is considered one of the Big Five American information technology companies, along with Amazon, Google, Meta, and Microsoft. Apple was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in April 1976 to develop and sell Wozniak's Apple I personal computer. The company was incorporated by Jobs and Wozniak as Apple Computer Company a few months later, and sales of its computers, including the Apple II, grew quickly. Within a few years, they had evolved into a computer company with over a thousand employees and became the fastest-growing company in U.S. history at the time. Apple has expanded into designing and manufacturing consumer electronics, software, and online services. Apple is the world's largest technology company by revenue and, since January 2021, the world's most valuable company.",
                    "key_products": ["iPhone", "iPad", "Mac", "Apple Watch", "AirPods", "Apple TV", "HomePod"],
                    "stock_symbol": "AAPL"
                },
                {
                    "name": "Microsoft",
                    "industry": "Technology",
                    "founded": 1975,
                    "headquarters": "Redmond, Washington",
                    "employees": 221000,
                    "revenue": "211.9 billion USD",
                    "description": "Microsoft Corporation is an American multinational technology corporation which produces computer software, consumer electronics, personal computers, and related services. Its best-known software products are the Microsoft Windows line of operating systems, the Microsoft Office suite, and the Internet Explorer and Edge web browsers. Its flagship hardware products are the Xbox video game consoles and the Microsoft Surface lineup of touchscreen personal computers. Microsoft ranked No. 21 in the 2020 Fortune 500 rankings of the largest United States corporations by total revenue; it was the world's largest software maker by revenue as of 2019. It is considered one of the Big Five American information technology companies, alongside Google, Apple, Meta, and Amazon. Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975, to develop and sell BASIC interpreters for the Altair 8800. During the 1980s, it rose to dominate the personal computer operating system market with MS-DOS, followed by Windows.",
                    "key_products": ["Windows", "Office 365", "Azure", "Xbox", "Surface", "LinkedIn", "GitHub"],
                    "stock_symbol": "MSFT"
                },
                {
                    "name": "Tesla",
                    "industry": "Automotive",
                    "founded": 2003,
                    "headquarters": "Austin, Texas",
                    "employees": 127855,
                    "revenue": "96.8 billion USD",
                    "description": "Tesla, Inc. is an American multinational automotive and clean energy company headquartered in Austin, Texas. Tesla designs and manufactures electric vehicles, battery energy storage systems, solar panels and solar roof tiles, and related products and services. Tesla is one of the world's most valuable companies and is, as of 2023, the world's most valuable automaker. In 2021, the company had the most worldwide sales of battery electric vehicles and plug-in electric vehicles, capturing 21% of the battery-electric market and 14% of the plug-in market. Through its subsidiary Tesla Energy, the company develops and is a major installer of solar photovoltaic energy generation systems in the United States. Tesla Energy is also one of the largest global suppliers of battery energy storage systems, with 6.5 gigawatt-hours installed in 2022. The company was founded in 2003 by Martin Eberhard and Marc Tarpenning. The company is named after inventor and electrical engineer Nikola Tesla.",
                    "key_products": ["Model S", "Model 3", "Model X", "Model Y", "Cybertruck", "Tesla Energy", "Autopilot"],
                    "stock_symbol": "TSLA"
                },
                {
                    "name": "OpenAI",
                    "industry": "Artificial Intelligence",
                    "founded": 2015,
                    "headquarters": "San Francisco, California",
                    "employees": 1500,
                    "revenue": "1.6 billion USD",
                    "description": "OpenAI is an American artificial intelligence research laboratory consisting of the for-profit corporation OpenAI LP and its parent company, the non-profit OpenAI Inc. The company conducts research in the field of artificial intelligence with the stated goal of promoting and developing friendly AI in such a way as to benefit humanity as a whole. The organization was founded in San Francisco in late 2015 by Sam Altman, Reid Hoffman, Jessica Livingston, Elon Musk, Ilya Sutskever, Peter Thiel and others, who collectively pledged US$1 billion. Musk resigned from the board in February 2018 but remained a donor. In 2019, OpenAI LP received a US$1 billion investment from Microsoft. OpenAI is headquartered at the Pioneer Building in Mission District, San Francisco. OpenAI's research focuses on developing artificial general intelligence (AGI) that is safe and beneficial to humanity. The company has produced several influential AI models, including the GPT series of language models.",
                    "key_products": ["GPT-4", "ChatGPT", "DALL-E", "Codex", "Whisper", "GPT-3.5"],
                    "stock_symbol": "Private"
                },
                {
                    "name": "Meta",
                    "industry": "Technology",
                    "founded": 2004,
                    "headquarters": "Menlo Park, California",
                    "employees": 86482,
                    "revenue": "116.6 billion USD",
                    "description": "Meta Platforms, Inc., formerly named Facebook, Inc., is an American multinational technology conglomerate based in Menlo Park, California. The company owns Facebook, Instagram, and WhatsApp, among other products and services. Meta is one of the world's most valuable companies and among the ten largest publicly traded corporations in the United States. It is considered one of the Big Five American information technology companies, alongside Amazon, Google, Apple, and Microsoft. Meta's products and services include Facebook, Messenger, Facebook Watch, and Meta Portal. It has also acquired Instagram, WhatsApp, and Oculus. Facebook was founded by Mark Zuckerberg, along with fellow Harvard College students and roommates Eduardo Saverin, Andrew McCollum, Dustin Moskovitz, and Chris Hughes, originally as TheFacebook.com—today's Facebook, a popular global social networking website.",
                    "key_products": ["Facebook", "Instagram", "WhatsApp", "Messenger", "Oculus", "Meta Quest", "Horizon Worlds"],
                    "stock_symbol": "META"
                },
                {
                    "name": "Amazon",
                    "industry": "E-commerce",
                    "founded": 1994,
                    "headquarters": "Seattle, Washington",
                    "employees": 1541000,
                    "revenue": "513.9 billion USD",
                    "description": "Amazon.com, Inc. is an American multinational technology company which focuses on e-commerce, cloud computing, digital streaming, and artificial intelligence. It has been referred to as 'one of the most influential economic and cultural forces in the world', and is one of the world's most valuable brands. It is one of the Big Five American information technology companies, alongside Google, Apple, Meta, and Microsoft. Amazon was founded by Jeff Bezos from his garage in Bellevue, Washington, on July 5, 1994. Initially an online marketplace for books, it has expanded into a multitude of product categories: a strategy that has earned it the moniker The Everything Store. It has multiple subsidiaries including Amazon Web Services, Amazon Studios, Audible, Goodreads, IMDb, Kiva Systems, Shopbop, Teachstreet, Twitch, and Whole Foods Market. Amazon has separate retail websites for the United States, the United Kingdom and Ireland, France, Canada, Germany, Italy, Spain, Netherlands, Australia, Brazil, Japan, China, India, and Mexico.",
                    "key_products": ["Amazon Marketplace", "AWS", "Prime Video", "Alexa", "Kindle", "Echo", "Whole Foods"],
                    "stock_symbol": "AMZN"
                },
                {
                    "name": "Netflix",
                    "industry": "Entertainment",
                    "founded": 1997,
                    "headquarters": "Los Gatos, California",
                    "employees": 12800,
                    "revenue": "31.6 billion USD",
                    "description": "Netflix, Inc. is an American subscription streaming service and production company based in Los Gatos, California. Founded in 1997 by Reed Hastings and Marc Randolph in Scotts Valley, California, it operates in over 190 countries, and has its headquarters in Los Gatos, California. It is the world's largest streaming entertainment service with 238 million paid memberships in more than 190 countries enjoying TV series, documentaries and feature films across a wide variety of genres and languages. Members can play, pause and resume watching as much as they want, anytime, anywhere, and can change their plans at any time. The company started as a DVD-by-mail service in 1998, began streaming in 2007, and introduced original content production in 2012. Netflix has played a prominent role in independent film distribution, and is a member of the Motion Picture Association.",
                    "key_products": ["Netflix Streaming", "Netflix Originals", "Netflix Games", "Netflix Animation"],
                    "stock_symbol": "NFLX"
                }
            ]
            
            for company in companies_data:
                session.run(
                    """CREATE (:Company {
                        name: $name, 
                        industry: $industry, 
                        founded: $founded,
                        headquarters: $headquarters,
                        employees: $employees,
                        revenue: $revenue,
                        description: $description,
                        key_products: $key_products,
                        stock_symbol: $stock_symbol
                    })""",
                    **company
                )
            
            # Create people with rich biographical information
            people_data = [
                {
                    "name": "Sundar Pichai",
                    "role": "CEO",
                    "company": "Google",
                    "age": 51,
                    "education": "Stanford University (MS), University of Pennsylvania (MBA), Indian Institute of Technology Kharagpur (B.Tech)",
                    "nationality": "Indian-American",
                    "biography": "Sundar Pichai is an Indian-American business executive who is the chief executive officer of Alphabet Inc. and its subsidiary Google. Born in Madurai, India, Pichai earned his degree from Indian Institute of Technology Kharagpur in metallurgical engineering. Moving to the United States, he attained an M.S. from Stanford University in materials science and engineering, and further attained an MBA from the Wharton School of the University of Pennsylvania. Pichai began his career as a materials engineer. Following a short stint at Applied Materials, he joined McKinsey & Company as a management consultant. Pichai joined Google in 2004, where he led the product management and innovation efforts for a suite of Google's client software products, including Google Chrome and Chrome OS, as well as being largely responsible for Google Drive. He went on to oversee the development of other applications such as Gmail and Google Maps."
                },
                {
                    "name": "Tim Cook",
                    "role": "CEO",
                    "company": "Apple",
                    "age": 63,
                    "education": "Auburn University (BS), Duke University (MBA)",
                    "nationality": "American",
                    "biography": "Timothy Donald Cook is an American business executive who has been the chief executive officer of Apple Inc. since 2011. Cook previously served as the company's chief operating officer under its co-founder Steve Jobs. He is the first CEO of Apple to be openly gay. Cook joined Apple in March 1998 as a senior vice president for worldwide operations, and then served as the executive vice president for worldwide sales and operations. He was made the chief executive on August 24, 2011, prior to Jobs' death in October of that year. During his tenure as the chief executive, he has advocated for the political reformation of international and domestic surveillance, cybersecurity, corporate taxation, American manufacturing, and environmental preservation."
                },
                {
                    "name": "Satya Nadella",
                    "role": "CEO",
                    "company": "Microsoft",
                    "age": 57,
                    "education": "Mangalore University (BE), University of Wisconsin–Milwaukee (MS), University of Chicago (MBA)",
                    "nationality": "Indian-American",
                    "biography": "Satya Narayana Nadella is an Indian-American business executive who is the chairman and chief executive officer (CEO) of Microsoft, succeeding Steve Ballmer in 2014 as CEO and John W. Thompson in 2021 as chairman. Before becoming CEO, he was the executive vice president of Microsoft's cloud and enterprise group, responsible for building and running the company's computing platforms. Nadella has been credited for helping bring Microsoft's database, Windows Server and developer tools to its Azure cloud service. He has been instrumental in the development of the company's AI strategy."
                },
                {
                    "name": "Elon Musk",
                    "role": "CEO",
                    "company": "Tesla",
                    "age": 52,
                    "education": "University of Pennsylvania (BS, BA)",
                    "nationality": "South African-American",
                    "biography": "Elon Reeve Musk is a business magnate and investor. He is the founder, CEO and chief engineer of SpaceX; angel investor, CEO and product architect of Tesla, Inc.; founder of The Boring Company; co-founder of Neuralink and OpenAI; and owner of X Corp. Musk is the wealthiest person in the world. A centibillionaire, Musk's estimated net worth was around $180 billion as of 2023. Musk was born in Pretoria, South Africa, and briefly attended at the University of Pretoria before moving to Canada at age 18, acquiring citizenship through his Canadian-born mother. Two years later, he matriculated at Queen's University and transferred to the University of Pennsylvania, where he received bachelor's degrees in economics and physics."
                },
                {
                    "name": "Sam Altman",
                    "role": "CEO",
                    "company": "OpenAI",
                    "age": 39,
                    "education": "Stanford University (dropped out)",
                    "nationality": "American",
                    "biography": "Samuel Harris Altman is an American entrepreneur, investor, and programmer. He is the CEO of OpenAI and the former president of Y Combinator. Altman is considered to be one of the leading figures in the AI boom. He dropped out of Stanford University after two years and founded Loopt, a social networking mobile application. After Loopt's acquisition by Green Dot Corporation for $43.4 million in 2012, Altman joined Y Combinator as a part-time partner. In 2014, he became the president of Y Combinator. He left Y Combinator in 2019 to focus full-time on OpenAI, which he had co-founded in 2015."
                },
                {
                    "name": "Mark Zuckerberg",
                    "role": "CEO",
                    "company": "Meta",
                    "age": 39,
                    "education": "Harvard University (dropped out)",
                    "nationality": "American",
                    "biography": "Mark Elliot Zuckerberg is an American business magnate, computer programmer, and philanthropist. He co-founded the social media website Facebook and its parent company Meta Platforms (formerly Facebook, Inc.), of which he is executive chairman and CEO. Zuckerberg attended Harvard University, where he launched Facebook in February 2004 with his roommates Eduardo Saverin, Andrew McCollum, Dustin Moskovitz, and Chris Hughes. Originally launched for college students, Facebook attracted millions of users and expanded rapidly. Zuckerberg moved the company to Palo Alto, California, where it received its first major investment from PayPal co-founder Peter Thiel. The company went public in 2012 and by 2021, Facebook had over 2.9 billion monthly active users."
                },
                {
                    "name": "Andy Jassy",
                    "role": "CEO",
                    "company": "Amazon",
                    "age": 56,
                    "education": "Harvard University (AB, MBA)",
                    "nationality": "American",
                    "biography": "Andrew R. Jassy is an American business executive who has been the president and chief executive officer of Amazon since July 2021. He previously led Amazon Web Services (AWS) as its CEO from 2003 to 2021. Jassy is known for his role in developing AWS into the largest cloud computing platform in the world. Under his leadership, AWS became a major revenue driver for Amazon, generating significant profit margins. Before his role as CEO, Jassy held various positions within Amazon and was considered one of Jeff Bezos' closest lieutenants. He has been with Amazon since 1997, just three years after the company was founded."
                },
                {
                    "name": "Reed Hastings",
                    "role": "Co-CEO",
                    "company": "Netflix",
                    "age": 63,
                    "education": "Bowdoin College (BA), Stanford University (MS)",
                    "nationality": "American",
                    "biography": "Wilmot Reed Hastings Jr. is an American billionaire business executive. He is the co-founder, chairman, and co-chief executive officer of Netflix, and on the boards of Facebook and a number of non-profit organizations. A former member of the California State Board of Education, Hastings is an advocate for education reform through charter schools. Hastings founded Netflix in 1997. Under his leadership, Netflix transitioned from a DVD-by-mail service to a global streaming platform and major content producer. He has been instrumental in Netflix's international expansion and its move into original content creation."
                }
            ]
            
            for person in people_data:
                # Create person with rich data
                session.run(
                    """CREATE (:Person {
                        name: $name, 
                        role: $role,
                        age: $age,
                        education: $education,
                        nationality: $nationality,
                        biography: $biography
                    })""",
                    name=person["name"], role=person["role"],
                    age=person["age"], education=person["education"],
                    nationality=person["nationality"], biography=person["biography"]
                )
                # Create relationship with company
                session.run(
                    """
                    MATCH (p:Person {name: $person_name}), (c:Company {name: $company_name})
                    CREATE (p)-[:WORKS_AT]->(c)
                    """,
                    person_name=person["name"], company_name=person["company"]
                )
            
            # Create research documents and papers
            documents_data = [
                {
                    "title": "Attention Is All You Need",
                    "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Lukasz Kaiser", "Illia Polosukhin"],
                    "year": 2017,
                    "venue": "Neural Information Processing Systems (NeurIPS)",
                    "type": "Research Paper",
                    "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature.",
                    "content": "The Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output. The Transformer allows for significantly more parallelization and can reach a new state of the art in translation quality after being trained for as little as twelve hours on eight P100 GPUs. In this work we present the Transformer, the first transduction model relying entirely on self-attention to compute representations of its input and output without using sequence-aligned RNNs or convolution. The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder, shown in the left and right halves of Figure 1, respectively. Multi-Head Attention allows the model to jointly attend to information from different representation subspaces at different positions.",
                    "citations": 45000,
                    "doi": "10.48550/arXiv.1706.03762"
                },
                {
                    "title": "Language Models are Few-Shot Learners",
                    "authors": ["Tom B. Brown", "Benjamin Mann", "Nick Ryder", "Melanie Subbiah", "OpenAI GPT-3 Team"],
                    "year": 2020,
                    "venue": "Neural Information Processing Systems (NeurIPS)",
                    "type": "Research Paper",
                    "abstract": "Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a large corpus of text followed by fine-tuning on a specific task. While typically task-agnostic in architecture, this method still requires task-specific fine-tuning datasets of thousands or tens of thousands of examples. By contrast, humans can generally perform a new language task from only a few examples or from simple instructions – something which current NLP systems still largely struggle with. Here we show that scaling up language models greatly improves task-agnostic, few-shot performance, sometimes even reaching competitiveness with prior state-of-the-art fine-tuning approaches.",
                    "content": "GPT-3 achieves strong performance on many NLP datasets, including translation, question-answering, and cloze tasks, as well as several tasks that require on-the-fly reasoning or domain adaptation, such as unscrambling words, using a novel word in a sentence, or performing 3-digit arithmetic. We find that GPT-3's performance scales with model size across a wide range of tasks, and that models with tens of billions of parameters can match the performance of fine-tuned systems on some tasks. We also find that larger models exhibit an improved ability to learn from context (in-context learning), and we demonstrate this ability on a number of diverse tasks.",
                    "citations": 12000,
                    "doi": "10.48550/arXiv.2005.14165"
                },
                {
                    "title": "Deep Learning",
                    "authors": ["Ian Goodfellow", "Yoshua Bengio", "Aaron Courville"],
                    "year": 2016,
                    "venue": "MIT Press",
                    "type": "Book",
                    "abstract": "Deep learning is a form of machine learning that enables computers to learn from experience and understand the world in terms of a hierarchy of concepts. Because the computer gathers knowledge from experience, there is no need for a human computer operator to formally specify all the knowledge that the computer needs. The hierarchy of concepts allows the computer to learn complicated concepts by building them out of simpler ones; a graph of these hierarchies would be many layers deep. This book introduces a broad range of topics in deep learning.",
                    "content": "The Deep Learning textbook is a resource intended to help students and practitioners enter the field of machine learning in general and deep learning in particular. The online version of the book is now complete and will remain available online for free. The deep learning textbook can now be ordered on Amazon. For up to date errata, see the errata page. If you notice a mistake or have a suggestion, please do not hesitate to write to us at feedback@deeplearningbook.org. Deep learning is a form of machine learning that enables computers to learn from experience and understand the world in terms of a hierarchy of concepts.",
                    "citations": 35000,
                    "doi": "N/A"
                },
                {
                    "title": "Tesla Autopilot: Full Self-Driving Capability Technical Report",
                    "authors": ["Tesla AI Team", "Andrej Karpathy", "Ashok Elluswamy"],
                    "year": 2022,
                    "venue": "Tesla Technical Report",
                    "type": "Technical Report",
                    "abstract": "This technical report describes Tesla's approach to autonomous driving, detailing the neural network architectures, training methodologies, and real-world deployment strategies used in Tesla Autopilot and Full Self-Driving (FSD) capability. The report covers the evolution from rule-based systems to end-to-end neural networks, the use of large-scale real-world driving data, and the challenges of scaling autonomous driving technology.",
                    "content": "Tesla's Autopilot represents one of the most advanced driver assistance systems currently deployed at scale. The system leverages a suite of cameras, ultrasonic sensors, and radar to provide 360-degree visibility around the vehicle. The neural networks powering Autopilot are trained on millions of miles of real-world driving data collected from Tesla's fleet. The architecture has evolved from modular, hand-engineered systems to increasingly end-to-end neural network approaches. Tesla's unique advantage lies in its ability to collect vast amounts of real-world driving data from its fleet of vehicles, enabling continuous improvement of the Autopilot system through over-the-air updates.",
                    "citations": 150,
                    "doi": "N/A"
                }
            ]
            
            for doc in documents_data:
                session.run(
                    """CREATE (:Document {
                        title: $title,
                        authors: $authors,
                        year: $year,
                        venue: $venue,
                        type: $type,
                        abstract: $abstract,
                        content: $content,
                        citations: $citations,
                        doi: $doi
                    })""",
                    **doc
                )
            
            # Create topics and discussions with enhanced content
            topics_data = [
                {
                    "name": "Artificial Intelligence",
                    "description": "AI research and development",
                    "content": "Artificial Intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of 'intelligent agents': any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. Colloquially, the term 'artificial intelligence' is often used to describe machines that mimic cognitive functions that humans associate with the human mind, such as learning and problem solving. As machines become increasingly capable, tasks considered to require intelligence are often removed from the definition of AI, a phenomenon known as the AI effect.",
                    "applications": ["Natural Language Processing", "Computer Vision", "Robotics", "Expert Systems", "Machine Learning"],
                    "key_researchers": ["Alan Turing", "John McCarthy", "Marvin Minsky", "Geoffrey Hinton", "Yann LeCun"]
                },
                {
                    "name": "Machine Learning",
                    "description": "ML algorithms and applications",
                    "content": "Machine learning (ML) is a field of inquiry devoted to understanding and building methods that 'learn', that is, methods that leverage data to improve performance on some set of tasks. It is seen as a part of artificial intelligence. Machine learning algorithms build a model based on training data in order to make predictions or decisions without being explicitly programmed to do so. Machine learning algorithms are used in a wide variety of applications, such as in medicine, email filtering, speech recognition, and computer vision, where it is difficult or unfeasible to develop conventional algorithms to perform the needed tasks.",
                    "applications": ["Supervised Learning", "Unsupervised Learning", "Reinforcement Learning", "Deep Learning", "Neural Networks"],
                    "key_researchers": ["Arthur Samuel", "Tom Mitchell", "Andrew Ng", "Ian Goodfellow", "Yoshua Bengio"]
                },
                {
                    "name": "Cloud Computing",
                    "description": "Cloud infrastructure and services",
                    "content": "Cloud computing is the on-demand availability of computer system resources, especially data storage and computing power, without direct active management by the user. Large clouds often have functions distributed over multiple locations, each location being a data center. Cloud computing relies on sharing of resources to achieve coherence and typically using a 'pay-as-you-go' model which can help in reducing capital expenses but may also lead to unexpected operating expenses for unaware users.",
                    "applications": ["Infrastructure as a Service", "Platform as a Service", "Software as a Service", "Serverless Computing", "Container Orchestration"],
                    "key_researchers": ["Eric Schmidt", "John McCarthy", "J.C.R. Licklider"]
                },
                {
                    "name": "Electric Vehicles",
                    "description": "EV technology and market",
                    "content": "An electric vehicle (EV) is a vehicle that uses one or more electric motors for propulsion. It can be powered by a collector system, with electricity from extravehicular sources, or it can be powered autonomously by a battery. EVs include, but are not limited to, road and rail vehicles, surface and underwater vessels, electric aircraft and electric spacecraft. The term also refers to hybrid electric vehicles which combine a conventional internal combustion engine with an electric propulsion system.",
                    "applications": ["Battery Technology", "Charging Infrastructure", "Autonomous Driving", "Energy Storage", "Sustainable Transportation"],
                    "key_researchers": ["Elon Musk", "John Goodenough", "Akira Yoshino", "Stanley Whittingham"]
                }
            ]
            
            for topic in topics_data:
                session.run(
                    """CREATE (:Topic {
                        name: $name, 
                        description: $description,
                        content: $content,
                        applications: $applications,
                        key_researchers: $key_researchers
                    })""",
                    **topic
                )
            
            # Create relationships between companies and topics
            company_topic_relations = [
                ("Google", "Artificial Intelligence", "RESEARCHES"),
                ("Google", "Cloud Computing", "PROVIDES"),
                ("Apple", "Mobile Technology", "DEVELOPS"),
                ("Microsoft", "Cloud Computing", "PROVIDES"),
                ("Microsoft", "Artificial Intelligence", "RESEARCHES"),
                ("Tesla", "Electric Vehicles", "MANUFACTURES"),
                ("OpenAI", "Artificial Intelligence", "RESEARCHES"),
                ("OpenAI", "Machine Learning", "DEVELOPS"),
                ("Meta", "Social Media", "OPERATES"),
                ("Meta", "Artificial Intelligence", "RESEARCHES"),
                ("Amazon", "E-commerce", "OPERATES"),
                ("Amazon", "Cloud Computing", "PROVIDES"),
                ("Netflix", "Streaming Technology", "PROVIDES")
            ]
            
            for company, topic, relation in company_topic_relations:
                session.run(
                    f"""
                    MATCH (c:Company {{name: $company}}), (t:Topic {{name: $topic}})
                    CREATE (c)-[:{relation}]->(t)
                    """,
                    company=company, topic=topic
                )
            
            # Create relationships between documents and topics
            document_topic_relations = [
                ("Attention Is All You Need", "Artificial Intelligence", "RELATES_TO"),
                ("Attention Is All You Need", "Machine Learning", "RELATES_TO"),
                ("Language Models are Few-Shot Learners", "Artificial Intelligence", "RELATES_TO"),
                ("Language Models are Few-Shot Learners", "Machine Learning", "RELATES_TO"),
                ("Deep Learning", "Artificial Intelligence", "RELATES_TO"),
                ("Deep Learning", "Machine Learning", "RELATES_TO"),
                ("Tesla Autopilot: Full Self-Driving Capability Technical Report", "Electric Vehicles", "RELATES_TO"),
                ("Tesla Autopilot: Full Self-Driving Capability Technical Report", "Artificial Intelligence", "RELATES_TO")
            ]
            
            for doc_title, topic_name, relation in document_topic_relations:
                session.run(
                    """
                    MATCH (d:Document {title: $doc_title}), (t:Topic {name: $topic_name})
                    CREATE (d)-[:RELATES_TO]->(t)
                    """,
                    doc_title=doc_title, topic_name=topic_name
                )
            
            # Create relationships between companies/people and documents
            company_document_relations = [
                ("OpenAI", "Language Models are Few-Shot Learners", "PUBLISHED"),
                ("Tesla", "Tesla Autopilot: Full Self-Driving Capability Technical Report", "PUBLISHED"),
                ("Google", "Attention Is All You Need", "PUBLISHED")
            ]
            
            for company, doc_title, relation in company_document_relations:
                session.run(
                    """
                    MATCH (c:Company {name: $company}), (d:Document {title: $doc_title})
                    CREATE (c)-[:PUBLISHED]->(d)
                    """,
                    company=company, doc_title=doc_title
                )
            
            # Create some collaboration relationships
            collaborations = [
                ("Google", "OpenAI", "COLLABORATES_WITH"),
                ("Microsoft", "OpenAI", "PARTNERS_WITH"),
                ("Apple", "Google", "COMPETES_WITH"),
                ("Tesla", "Google", "COLLABORATES_WITH"),
                ("Meta", "Microsoft", "COMPETES_WITH")
            ]
            
            for company1, company2, relation in collaborations:
                if relation == "COLLABORATES_WITH":
                    session.run(
                        """
                        MATCH (c1:Company {name: $company1}), (c2:Company {name: $company2})
                        CREATE (c1)-[:COLLABORATES_WITH]->(c2)
                        """,
                        company1=company1, company2=company2
                    )
                elif relation == "PARTNERS_WITH":
                    session.run(
                        """
                        MATCH (c1:Company {name: $company1}), (c2:Company {name: $company2})
                        CREATE (c1)-[:PARTNERS_WITH]->(c2)
                        """,
                        company1=company1, company2=company2
                    )
                elif relation == "COMPETES_WITH":
                    session.run(
                        """
                        MATCH (c1:Company {name: $company1}), (c2:Company {name: $company2})
                        CREATE (c1)-[:COMPETES_WITH]->(c2)
                        """,
                        company1=company1, company2=company2
                    )
            
        logger.info("Sample data created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")
        raise

def verify_data():
    """Verify that data was loaded correctly"""
    try:
        with db.driver.session() as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN labels(n) as label, count(n) as count")
            logger.info("Data verification:")
            for record in result:
                logger.info(f"  {record['label'][0] if record['label'] else 'Unknown'}: {record['count']} nodes")
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count")
            logger.info("Relationships:")
            for record in result:
                logger.info(f"  {record['rel_type']}: {record['count']} relationships")
                
    except Exception as e:
        logger.error(f"Failed to verify data: {e}")
        raise

def load_sample_data():
    """Main function to load sample data"""
    logger.info("Starting sample data loading...")
    
    try:
        # Test database connection
        health = db.health_check()
        if health["status"] != "ok":
            raise Exception(f"Database health check failed: {health}")
        
        # Clear and load data
        clear_database()
        create_sample_data()
        verify_data()
        
        logger.info("Sample data loading completed successfully!")
        
    except Exception as e:
        logger.error(f"Sample data loading failed: {e}")
        raise
    finally:
        # Close database connection
        db.close()

if __name__ == "__main__":
    load_sample_data()