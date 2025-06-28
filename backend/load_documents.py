import logging
from dotenv import load_dotenv
load_dotenv()

from vector_store import chroma_service
from database import db

logger = logging.getLogger(__name__)

def load_investment_documents():
    """Load sample investment and business documents into ChromaDB"""
    
    documents = [
        {
            "title": "Apple's 2025 Investment Strategy: AI and Healthcare Focus",
            "content": """Apple Inc. announced its comprehensive investment strategy for 2025, with a primary focus on artificial intelligence and healthcare technologies. The company plans to allocate $15 billion towards AI research and development, particularly in areas of on-device processing and privacy-preserving machine learning.

Key Investment Areas:
1. AI and Machine Learning: $15B allocation for developing next-generation AI chips and software frameworks
2. Healthcare Technology: $8B investment in health monitoring devices and digital health platforms
3. Autonomous Systems: $5B for self-driving car technology and robotics
4. Sustainable Energy: $3B for renewable energy infrastructure and battery technology
5. Augmented Reality: $4B for AR/VR hardware and ecosystem development

Strategic Partnerships:
- Partnership with OpenAI for integrating advanced language models into iOS ecosystem
- Collaboration with major healthcare providers for health data analytics
- Joint ventures with automotive companies for Apple Car development
- Investment in renewable energy companies for carbon neutrality goals

The investment strategy reflects Apple's commitment to maintaining technological leadership while expanding into new markets. CEO Tim Cook emphasized the importance of privacy-first AI development and sustainable technology solutions.

Market analysts predict these investments will drive significant revenue growth, with projected returns of 15-20% annually. The healthcare technology sector alone is expected to contribute $50B in revenue by 2027.

Apple's R&D spending has increased by 40% compared to 2024, demonstrating the company's confidence in these emerging technologies. The company also announced plans to acquire several AI startups and health technology companies to accelerate development timelines.""",
            "metadata": {
                "type": "investment_report",
                "date": "2025-01-15",
                "source": "Apple Inc. Investor Relations",
                "companies": "Apple, OpenAI",
                "topics": "artificial intelligence, healthcare, investment, strategy",
                "amount": "$35B total investment",
                "year": 2025,
                "authors": "Apple Strategy Team"
            }
        },
        {
            "title": "Microsoft's Cloud Infrastructure Expansion Plan 2025",
            "content": """Microsoft Corporation unveiled its ambitious cloud infrastructure expansion plan for 2025, targeting global market dominance in cloud computing services. The company will invest $20 billion in new data centers, AI infrastructure, and edge computing capabilities.

Investment Breakdown:
- Data Center Expansion: $12B for 50 new data centers across North America, Europe, and Asia
- AI Infrastructure: $5B for specialized AI training and inference hardware
- Edge Computing: $2B for edge computing nodes and 5G integration
- Cybersecurity: $1B for advanced threat detection and zero-trust architecture

Geographic Focus:
- North America: 20 new data centers
- Europe: 15 new data centers  
- Asia-Pacific: 12 new data centers
- Latin America: 3 new data centers

Strategic Objectives:
1. Reduce latency for Azure customers globally
2. Support growing demand for AI and machine learning workloads
3. Enhance edge computing capabilities for IoT applications
4. Strengthen cybersecurity offerings
5. Achieve carbon negative operations by 2026

Microsoft expects this investment to increase Azure's market share from 21% to 28% by end of 2025. The company is also partnering with renewable energy providers to power all new data centers with clean energy.

CEO Satya Nadella stated: "This investment represents our commitment to empowering every organization on the planet to achieve more through cloud technology and artificial intelligence."

The expansion will create approximately 15,000 new jobs globally, including cloud architects, AI engineers, and cybersecurity specialists. Microsoft is also investing in local talent development programs in each region.""",
            "metadata": {
                "type": "expansion_plan",
                "date": "2025-01-20",
                "source": "Microsoft Corporation",
                "companies": "Microsoft",
                "topics": "cloud computing, artificial intelligence, infrastructure, expansion",
                "amount": "$20B investment",
                "year": 2025,
                "authors": "Microsoft Strategy Division"
            }
        },
        {
            "title": "Tesla's Energy Storage and Solar Investment Initiative",
            "content": """Tesla Inc. announced a $12 billion investment initiative focused on energy storage systems and solar technology for 2025-2027. This represents the company's largest commitment to sustainable energy infrastructure beyond electric vehicles.

Investment Components:
1. Gigafactory Expansion: $7B for three new Gigafactories dedicated to battery production
2. Solar Panel Manufacturing: $3B for advanced solar cell technology and manufacturing facilities
3. Energy Storage Systems: $2B for utility-scale battery storage projects

New Gigafactory Locations:
- Texas (Austin): $2.5B investment, focused on utility-scale batteries
- Nevada (Expansion): $2B additional investment for increased battery production
- Germany (Berlin): $1.5B for European energy storage market
- India (Bangalore): $1B for Asian market expansion

Technology Focus:
- Next-generation 4680 battery cells with improved energy density
- Perovskite-silicon solar cells achieving 30% efficiency
- AI-powered energy management systems for grid optimization
- Vehicle-to-grid technology integration

Market Opportunity:
The global energy storage market is projected to grow from $15B in 2024 to $75B by 2030. Tesla aims to capture 25% market share through this investment.

Environmental Impact:
These initiatives are expected to:
- Reduce global CO2 emissions by 50 million tons annually
- Enable 100 GW of renewable energy storage capacity
- Power 10 million homes with clean energy

CEO Elon Musk emphasized: "Sustainable energy is the future, and Tesla is investing heavily to accelerate the world's transition to sustainable energy."

The company is also partnering with utility companies and governments worldwide to deploy large-scale energy storage projects. Several pilot projects are already underway in California, Texas, and Australia.""",
            "metadata": {
                "type": "sustainability_investment",
                "date": "2025-01-25",
                "source": "Tesla Inc.",
                "companies": "Tesla",
                "topics": "energy storage, solar technology, sustainability, gigafactory",
                "amount": "$12B investment",
                "year": 2025,
                "authors": "Tesla Energy Division"
            }
        },
        {
            "title": "Meta's Metaverse and AR Infrastructure Investment 2025",
            "content": """Meta Platforms Inc. revealed its $18 billion investment plan for metaverse and augmented reality infrastructure in 2025, marking the company's continued commitment to virtual reality technologies.

Investment Allocation:
- VR/AR Hardware Development: $8B for next-generation headsets and smart glasses
- Metaverse Platform Development: $5B for virtual world creation tools and infrastructure
- AI for Virtual Environments: $3B for realistic avatar and environment generation
- Creator Economy: $2B for supporting content creators and developers

Key Projects:
1. Meta Quest 4: Advanced VR headset with 4K resolution per eye
2. Ray-Ban Meta Smart Glasses: AR capabilities with AI assistant integration
3. Horizon Worlds Expansion: Enhanced virtual reality social platform
4. Workplace VR: Enterprise-focused virtual collaboration tools

Technology Innovations:
- Haptic feedback systems for immersive experiences
- Eye tracking and facial expression recognition
- Spatial computing and 3D environment mapping
- Real-time language translation in virtual spaces

Market Strategy:
Meta aims to onboard 1 billion users to metaverse platforms by 2027. The company is targeting both consumer and enterprise markets, with special focus on:
- Virtual meetings and remote work
- Educational and training applications  
- Gaming and entertainment experiences
- Social interaction and community building

Partnerships and Collaborations:
- Microsoft: Integration with Office 365 for workplace VR
- NVIDIA: AI-powered graphics and rendering technology
- Qualcomm: Custom chipsets for AR/VR devices
- Educational institutions: VR learning platform development

CEO Mark Zuckerberg stated: "The metaverse represents the next evolution of social technology, and we're investing heavily to build the infrastructure that will power virtual experiences for billions of people."

The investment is expected to generate significant revenue streams by 2026, with projections of $15B annual revenue from metaverse-related products and services.""",
            "metadata": {
                "type": "technology_investment",
                "date": "2025-02-01",
                "source": "Meta Platforms Inc.",
                "companies": "Meta, Microsoft, NVIDIA, Qualcomm",
                "topics": "metaverse, virtual reality, augmented reality, social technology",
                "amount": "$18B investment",
                "year": 2025,
                "authors": "Meta Reality Labs"
            }
        },
        {
            "title": "Google's AI Research and Quantum Computing Investment",
            "content": """Alphabet Inc.'s Google announced a groundbreaking $25 billion investment in artificial intelligence research and quantum computing for 2025-2026, representing the largest single investment in emerging technologies by any tech company.

Investment Breakdown:
- AI Research and Development: $15B for foundation models and specialized AI applications
- Quantum Computing: $8B for quantum processor development and quantum algorithms
- AI Infrastructure: $2B for training clusters and inference optimization

AI Research Focus Areas:
1. Multimodal AI Models: Advanced systems processing text, images, video, and audio
2. Scientific AI: AI for drug discovery, climate modeling, and materials science
3. Responsible AI: Safety, ethics, and bias mitigation research
4. Edge AI: Efficient models for mobile and IoT devices

Quantum Computing Milestones:
- 1000-qubit quantum processor by end of 2025
- Quantum advantage in optimization problems
- Quantum-AI hybrid algorithms for machine learning
- Quantum internet prototype network

Strategic Applications:
- Healthcare: AI-driven drug discovery and personalized medicine
- Climate: AI models for weather prediction and carbon capture optimization
- Finance: Quantum algorithms for risk analysis and portfolio optimization
- Transportation: AI for autonomous vehicle safety and traffic optimization

Research Partnerships:
- Stanford University: $500M for AI safety research center
- MIT: $300M for quantum-AI research collaboration
- Oxford University: $200M for responsible AI development
- Top global universities: $1B for distributed research network

Talent Acquisition:
Google plans to hire 10,000 AI researchers and engineers globally, including:
- 3,000 PhD-level AI researchers
- 4,000 machine learning engineers
- 2,000 quantum computing specialists
- 1,000 AI ethics and safety experts

CEO Sundar Pichai emphasized: "This investment will accelerate breakthroughs that benefit humanity while maintaining our commitment to AI safety and responsible development."

Expected outcomes include revolutionary advances in healthcare, climate solutions, and scientific discovery, with potential to solve some of humanity's greatest challenges.""",
            "metadata": {
                "type": "research_investment",
                "date": "2025-02-05",
                "source": "Google/Alphabet Inc.",
                "companies": "Google, Alphabet",
                "topics": "artificial intelligence, quantum computing, research, technology",
                "amount": "$25B investment",
                "year": 2025,
                "authors": "Google Research",
                "venue": "Google I/O Developer Conference"
            }
        },
        {
            "title": "Amazon's Logistics and Robotics Automation Investment",
            "content": """Amazon.com Inc. unveiled its comprehensive $16 billion investment in logistics automation and robotics for 2025, aimed at revolutionizing e-commerce fulfillment and delivery systems.

Investment Categories:
- Warehouse Robotics: $8B for automated sorting, picking, and packing systems
- Delivery Innovation: $4B for drone delivery and autonomous vehicle fleets
- AI-Powered Logistics: $3B for predictive analytics and supply chain optimization  
- Employee Training: $1B for workforce transition and upskilling programs

Robotics Infrastructure:
1. Automated Fulfillment Centers: 500 new robotic facilities worldwide
2. Robotic Pick and Pack Systems: AI-powered robots for order processing
3. Autonomous Mobile Robots: Self-navigating robots for warehouse operations
4. Collaborative Robots: Human-robot teams for complex tasks

Delivery Innovation Projects:
- Prime Air Drone Delivery: Expansion to 50 metropolitan areas
- Amazon Scout Delivery Robots: Autonomous sidewalk delivery vehicles
- Electric Delivery Vans: 100,000 custom electric vehicles by Rivian
- Micro-Fulfillment Centers: Small automated warehouses in urban areas

AI and Machine Learning Applications:
- Demand Forecasting: Predicting customer orders with 95% accuracy
- Route Optimization: AI-powered delivery route planning
- Inventory Management: Automated restocking and distribution
- Quality Control: Computer vision for product inspection

Global Expansion:
- North America: 200 new automated facilities
- Europe: 150 new robotic warehouses
- Asia-Pacific: 100 automated centers
- Latin America: 50 new facilities

Workforce Impact:
Amazon commits to retraining 1 million employees for higher-skilled roles, including:
- Robotics technicians and maintenance specialists
- AI and machine learning engineers
- Logistics optimization analysts
- Customer experience specialists

Environmental Benefits:
- 40% reduction in packaging waste through optimized systems
- 50% decrease in delivery vehicle emissions
- 30% improvement in energy efficiency of fulfillment centers
- Carbon neutral delivery in 100 cities by 2026

CEO Andy Jassy stated: "This investment will create the most advanced logistics network in the world while creating better jobs for our employees and faster delivery for our customers."

The initiative is expected to reduce delivery times to same-day standard for 80% of Prime members globally.""",
            "metadata": {
                "type": "automation_investment",
                "date": "2025-02-10",
                "source": "Amazon.com Inc.",
                "companies": "Amazon, Rivian",
                "topics": "logistics, robotics, automation, delivery",
                "amount": "$16B investment",
                "year": 2025,
                "authors": "Amazon Operations Team"
            }
        },
        {
            "title": "Netflix Content and Technology Investment Strategy 2025",
            "content": """Netflix Inc. announced its ambitious $20 billion content and technology investment strategy for 2025, focusing on original content production, gaming, and immersive entertainment technologies.

Investment Allocation:
- Original Content Production: $14B for movies, series, and documentaries
- Gaming Platform Development: $3B for cloud gaming and interactive content
- Technology Infrastructure: $2B for streaming optimization and AI recommendations
- International Expansion: $1B for local content in emerging markets

Content Strategy:
1. Premium Original Series: 150 new scripted series across all genres
2. Feature Films: 100 original movies including blockbuster productions
3. Documentary Programming: 50 documentary films and limited series
4. International Content: 200 local productions in 30+ countries
5. Interactive Entertainment: 25 interactive movies and choose-your-adventure content

Gaming Initiative:
- Cloud Gaming Platform: Netflix Games streaming service launch
- Mobile Gaming: 50 exclusive mobile games for subscribers
- Interactive Storytelling: Games based on popular Netflix series
- Gaming Studios: Acquisition of 5 game development studios

Technology Innovations:
- AI-Powered Recommendations: Advanced personalization algorithms
- 8K Streaming: Ultra-high-definition content delivery
- Spatial Audio: Immersive audio experiences for all content
- VR Content: Virtual reality experiences for select titles

Global Production Facilities:
- Hollywood: $2B for expanded studio facilities
- United Kingdom: $1B for European production hub
- South Korea: $500M for Asian content production
- Brazil: $300M for Latin American content
- India: $200M for Bollywood and regional content

Talent Partnerships:
Netflix is forming exclusive deals with:
- A-list directors and producers for tent-pole projects
- International creators for authentic local content
- Gaming industry veterans for interactive entertainment
- Technology partners for streaming innovation

Market Expansion:
- Africa: Launch in 15 new African markets
- Southeast Asia: Expansion to 8 additional countries
- Eastern Europe: 5 new market entries
- Enhanced accessibility features for global audiences

Subscriber Growth Projections:
Netflix aims to reach 300 million global subscribers by end of 2025, with revenue targets of $45 billion annually.

Co-CEO Ted Sarandos noted: "This investment represents our commitment to delivering unparalleled entertainment experiences while pioneering the future of interactive and immersive content."

The strategy includes sustainability initiatives to achieve carbon neutrality across all productions by 2026.""",
            "metadata": {
                "type": "content_investment",
                "date": "2025-02-15",
                "source": "Netflix Inc.",
                "companies": "Netflix",
                "topics": "streaming, content production, gaming, entertainment",
                "amount": "$20B investment",
                "year": 2025,
                "authors": "Netflix Content Team",
                "venue": "Netflix Investor Day"
            }
        }
    ]
    
    # Clear existing documents
    logger.info("Clearing existing documents...")
    chroma_service.clear_collection()
    
    # Load new documents
    logger.info("Loading investment documents...")
    for doc in documents:
        try:
            doc_id = chroma_service.add_document(
                title=doc["title"],
                content=doc["content"],
                metadata=doc["metadata"]
            )
            logger.info(f"Added document: {doc['title']}")
        except Exception as e:
            logger.error(f"Failed to add document {doc['title']}: {e}")
    
    # Verify loading
    stats = chroma_service.get_collection_stats()
    logger.info(f"Successfully loaded {stats['document_count']} documents")

def add_company_relationships():
    """Add relationships between companies mentioned in documents to Neo4j"""
    try:
        with db.driver.session() as session:
            # Add investment relationships
            investments = [
                ("Apple", "OpenAI", "PARTNERS_WITH", {"type": "AI Integration", "year": 2025}),
                ("Microsoft", "OpenAI", "INVESTS_IN", {"amount": "$10B", "year": 2023}),
                ("Meta", "Microsoft", "COLLABORATES_WITH", {"area": "Enterprise VR", "year": 2025}),
                ("Meta", "NVIDIA", "PARTNERS_WITH", {"area": "AI Graphics", "year": 2025}),
                ("Meta", "Qualcomm", "COLLABORATES_WITH", {"area": "AR Chips", "year": 2025}),
                ("Amazon", "Rivian", "INVESTS_IN", {"amount": "$1.3B", "area": "Electric Vehicles"}),
                ("Google", "Stanford University", "FUNDS", {"amount": "$500M", "area": "AI Safety"}),
                ("Google", "MIT", "FUNDS", {"amount": "$300M", "area": "Quantum-AI"}),
            ]
            
            for company1, company2, rel_type, properties in investments:
                # Check if companies exist, if not create them
                session.run("""
                    MERGE (c1:Company {name: $company1})
                    MERGE (c2:Company {name: $company2})
                """, company1=company1, company2=company2)
                
                # Create relationship
                if rel_type == "PARTNERS_WITH":
                    session.run("""
                        MATCH (c1:Company {name: $company1}), (c2:Company {name: $company2})
                        MERGE (c1)-[r:PARTNERS_WITH]->(c2)
                        SET r += $props
                    """, company1=company1, company2=company2, props=properties)
                elif rel_type == "INVESTS_IN":
                    session.run("""
                        MATCH (c1:Company {name: $company1}), (c2:Company {name: $company2})
                        MERGE (c1)-[r:INVESTS_IN]->(c2)
                        SET r += $props
                    """, company1=company1, company2=company2, props=properties)
                elif rel_type == "COLLABORATES_WITH":
                    session.run("""
                        MATCH (c1:Company {name: $company1}), (c2:Company {name: $company2})
                        MERGE (c1)-[r:COLLABORATES_WITH]->(c2)
                        SET r += $props
                    """, company1=company1, company2=company2, props=properties)
                elif rel_type == "FUNDS":
                    session.run("""
                        MATCH (c1:Company {name: $company1})
                        MERGE (org:Organization {name: $company2})
                        MERGE (c1)-[r:FUNDS]->(org)
                        SET r += $props
                    """, company1=company1, company2=company2, props=properties)
            
            logger.info("Added company relationships to Neo4j")
            
    except Exception as e:
        logger.error(f"Failed to add company relationships: {e}")

if __name__ == "__main__":
    logger.info("Starting document loading process...")
    
    # Load documents into ChromaDB
    load_investment_documents()
    
    # Add relationships to Neo4j
    add_company_relationships()
    
    logger.info("Document loading completed!")