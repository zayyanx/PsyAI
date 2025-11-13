# PsyAI

PsyAI is an open-source framework that aims to build a seamless switchover service between human experts and reviewers with their AI agent counterparts in Agentic workflows.

Building off the work done on the [Centaur Foundation Model](https://arxiv.org/abs/2410.20268) created by a team from the Institute for Human-Centered AI at Helmholtz Munich, PsyAI aims to use this 'foundation model for human cognition' to make transitions between humans and AI agents more seamless with a greatly reduced cognitive load. 

The primary hypothesis is as follows: If an LLM trained on psychology data predicts human decisions with >80% accuracy, then humans can make better decisions faster in agentic applications using a proxy agent framework. The secondary hypothesis being, expert users experiencing repetitive LLM training and decision-making workflows will benefit from a predictive decision framework that reduces decision fatigue and cognitive load.

Work on the PsyAI project aims to further research in the field of Human-in-the-loop applications, and LLM-as-a-judge amongst others. To that effect the PsyAI core team is working towards the goal of running a study in Q1 of 2026 with the outcome being a published paper on this subject. 

Currently, the team has slots open for additional members, contributors, and advisors on the core team, [inquire here](https://forms.gle/TCPKzSc9Z8H4m8LH7). Contributors to the codebase are always welcome under MIT creative commons licensing.


## High-Level Design

<img width="1620" height="914" alt="PsyAI High Level Design - Medical Context" src="https://github.com/zayyanx/PsyAI/blob/27d95f31116c7c87fac56084f686fb5f4721c850/Screenshot%202025-11-08%20at%205.44.25%20PM.png"/>

The ultimate goal of this project is to achieve seamless AI to Human conversations attuned on a subconscious level based on foundational components of human cognition.

## Project Structure

PsyAI is architected into two main layers:

### Platform Layer (Serial Development)
Core infrastructure built sequentially with dependencies:
1. **Core Infrastructure** - Configuration, logging, utilities
2. **LangChain/LangGraph Integration** - Agentic workflow orchestration
3. **LangSmith Integration** - Observability and evaluation
4. **Centaur Model Integration** - Decision alignment prediction
5. **Storage Layer** - Database and caching
6. **API Framework** - REST and WebSocket APIs

### Feature Layer (Parallel Development)
Independent features built on the platform:
- **Chat** - Multi-mode chat (AI, Expert, Passthrough)
- **Evals** - LangSmith evaluations with RAG
- **Human-in-the-Loop** - Review workflow for failed evals
- **Confidence Score** - Centaur-based decision confidence

## Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Quick start guide for developers
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system architecture
- **[ROADMAP.md](ROADMAP.md)** - Development timeline and build plan

## Technology Stack

- **Languages:** Python 3.11+
- **Frameworks:** FastAPI, LangChain, LangGraph, LangSmith
- **AI/ML:** OpenAI, Centaur Foundation Model
- **Storage:** PostgreSQL, Redis, Chroma/Pinecone/Weaviate
- **DevOps:** Docker, pytest, GitHub Actions

## Quick Start

```bash
# Clone repository
git clone https://github.com/zayyanx/PsyAI.git
cd PsyAI

# Run setup script
bash scripts/setup_dev.sh

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start services
cd docker && docker-compose up -d

# Run tests
pytest
```

For detailed setup instructions, see [GETTING_STARTED.md](GETTING_STARTED.md).

## Contributing

We welcome contributions! The project is in active development:

- **Current Phase:** Platform Development (Weeks 1-8)
- **Coming Soon:** Feature Development (Weeks 9-12)

See [GETTING_STARTED.md](GETTING_STARTED.md) for contribution guidelines and development workflow.

## Timeline

- **Weeks 1-8:** Platform development (serial)
- **Weeks 9-12:** Feature development (parallel)
- **Weeks 13-15:** Integration and testing
- **Q1 2026:** Research study launch

See [ROADMAP.md](ROADMAP.md) for detailed timeline.

## License

MIT License - See LICENSE file for details
