<img src="assets/godsinwhite_team.png" alt="" width="400"/>

# Corpus Analytica GodsinWhite

Corpus Analytica GodsinWhite is an advanced medical AI platform and your personal gateway to advanced medical diagnostics—powered by AI and backed by real medical expertise. Designed for patients, healthcare professionals, and curious minds alike, this platform provides a powerful, multi-agent AI interface for medical assistance, diagnostics, image analysis, and research that transforms how medical images are analyzed and understood.

## Overview

Built on the Agno framework, Corpus Analytica GodsinWhite orchestrates a team of specialized medical AI agents through the HALO Agent Interface (HALO). Each agent brings unique capabilities to the platform, from medical image analysis and PubMed research to data visualization and medical calculations.

The platform features a modern, intuitive Streamlit interface with both light and dark themes, real-time streaming responses, and comprehensive medical knowledge integration through vector databases.

# Corpus Analytica - Your Trusted Partner in Healthcare

At [Corpus Analytica](https://www.corpusanalytica.com), we redefine how medical professionals and patients connect—through a platform built for simplicity, security, and global reach.

#### What We Offer:
- Seamless Connections: We unite doctors, specialists, and patients through our cutting-edge digital platform.

- Expert Second Opinions: Gain easy access to a network of certified physicians and specialists for reliable second opinions.

- Effortless Booking: Our intuitive interface makes requesting and scheduling consultations fast and frustration-free.

- Global Access: Wherever you are, our online consultations bring expert medical advice right to your screen.

- Data You Can Trust: We uphold the highest standards in data protection and patient privacy—because your health deserves nothing less.

#### Experience Healthcare in a New Dimension
Your health is invaluable. With Corpus Analytica, discover a smarter, safer, and more connected way to care.

> *"Healthcare should be accessible, transparent, and empowering. At Corpus Analytica, we're building more than just a platform—we're building trust, one consultation at a time."* — Bernhard Z., Founder of [Corpus Analytica](https://www.corpusanalytica.com)


## Live Demo

Take a look at the [live demo here](https://godsinwhite.streamlit.app/)


## Features

- 🏥 **Medical AI Focus**: Specialized agents and tools designed for healthcare applications
- 🤖 **Multi-Agent Orchestration**: Coordinate multiple medical AI agents through the HALO Agent Interface
- 🧠 **Medical Knowledge Integration**: Access and utilize extensive medical knowledge bases with LanceDB vector storage
- 🔬 **Medical Image Analysis**: Comprehensive analysis of medical images with structured reporting
- 📊 **PubMed Integration**: Direct access to medical research literature and evidence-based context
- 💾 **Secure Session Management**: HIPAA-compliant conversation and data storage with SQLite
- 🎨 **Intuitive Medical UI**: Clean, responsive interface with light/dark theme support
- 🤝 **Collaborative Care**: Enable seamless communication between specialized medical AI agents

## System Requirements

- Python 3.8 or higher
- Git (for cloning the repository)
- Internet connection for API access

## Installation

1. **Clone the Repository**

```bash
git clone https://github.com/aizech/corpus-analytica-godsinwhite
cd corpus-analytica-godsinwhite
```

2. **Set Up Virtual Environment**

Using venv (recommended):
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**

**Important:** In the configuration page you can bring your own API keys.

Alternatively, you can create a `.env` file in the project root and configure your API keys:

```env
OPENAI_API_KEY=your_openai_key
```

5. **Launch the Application**

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501` by default.

## Project Structure

```
├── app.py              # Main Streamlit application entry point
├── pages/              # Additional Streamlit pages
│   ├── Home.py           # Main chat interface
│   ├── Medical_Image_Analysis.py  # Medical image analysis interface
│   ├── Experts_Chat.py   # Specialized medical expert consultation
│   ├── Generated_Images.py  # Gallery of generated images
│   ├── Configuration.py  # System settings
│   └── About.py          # Platform information
├── agents/              # Specialized agent implementations
│   ├── medical_agent.py  # Medical imaging expert
│   ├── pubmed_agent.py   # PubMed research agent
│   ├── data_analyst_agent.py  # Data analysis agent
│   └── visualizer_agent.py  # Visualization agent
├── tools/              # Custom tool implementations
├── assets/             # Static assets (images, icons)
├── halo.py             # HALO Agent Interface implementation
├── knowledge.py        # Knowledge base implementation
├── config.py           # Application configuration
├── utils.py            # Utility functions
├── knowledge_docs/     # Knowledge base documents
└── requirements.txt    # Project dependencies
```

## Configuration

The application can be configured through:

- `.env` file for API keys and sensitive data
- `config.py` for application settings
- `presets.json` for agent presets and configurations

## Specialized Medical Agents

GodsinWhite features a team of specialized AI agents, each with distinct medical capabilities:

### Medical Imaging Expert
- Analyzes various medical imaging modalities (X-ray, MRI, CT, Ultrasound)
- Provides structured analysis with technical assessment, professional analysis, and clinical interpretation
- Delivers patient-friendly explanations of medical findings
- Includes evidence-based context from medical literature

### PubMed Research Agent
- Searches and retrieves relevant medical literature from PubMed
- Summarizes research findings and clinical guidelines
- Provides evidence-based recommendations
- Connects imaging findings with current medical research

### Data Analysis Agent
- Processes and visualizes medical data
- Generates charts and graphs for healthcare analytics
- Analyzes trends and patterns in medical datasets
- Supports data-driven clinical decision making

### Medical Calculator Agent
- Performs medical calculations and risk assessments
- Implements standardized medical scoring systems
- Calculates dosages and conversions
- Provides evidence-based risk stratification

## Example Use Cases

1. **Medical Knowledge Assistance**
   - "What are the latest treatment guidelines for condition X?"
   - "Explain the differential diagnosis for these symptoms"
   - "Summarize recent research on this treatment method"

2. **Clinical Decision Support**
   - "Analyze these lab results and suggest possible diagnoses"
   - "Review this patient's history for potential drug interactions"
   - "Generate a preliminary assessment based on these symptoms"

3. **Healthcare Research**
   - "Find recent clinical trials related to this condition"
   - "Analyze treatment outcomes across different patient groups"
   - "Summarize the latest research in this medical field"

4. **Medical Documentation**
   - "Help structure this clinical note"
   - "Generate a template for this type of medical report"
   - "Assist in coding this medical procedure"

5. **Medical Image Analysis**
   - "Analyze this chest X-ray and identify any abnormalities"
   - "Review this MRI scan and describe the findings"
   - "Compare these two CT scans and highlight any changes"

## Support

For support and questions:
- Open an issue in the GitHub repository
- Check the documentation in the `docs` directory
- Join our community discussions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Medical Disclaimer

**Important:** GodsinWhite is designed for educational and demonstration purposes only. All medical analyses, suggestions, and information provided by this platform should be reviewed by qualified healthcare professionals before making any medical decisions.

The platform is not FDA-approved for clinical decision-making and should not replace professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Architecture Documentation

For detailed information about the system architecture and design decisions:

- **README_ADR.md**: Contains Architecture Decision Records (ADRs) and system architecture diagrams
- **README_PRD.md**: Contains the Product Requirements Document with detailed feature specifications

## Technical Stack

- **Framework**: [Agno](https://github.com/agno-ai/agno) for multi-agent AI orchestration
- **Frontend**: [Streamlit](https://streamlit.io/) for the web interface
- **AI Models**: OpenAI GPT models (GPT-4o, GPT-4o-mini, GPT-5)
- **Vector Database**: LanceDB for knowledge storage and retrieval
- **Session Storage**: SQLite (`halo_sessions.db` and `halo_memory.db`)

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Based on the Agno framework for multi-agent orchestration
- Powered by OpenAI models and APIs
- Integrated with PubMed for medical research

Open [localhost:8501](http://localhost:8501) to view your GodsinWhite interface.