# BGSTM - Professional Software Testing Framework

**BGSTM** (Better Global Software Testing Methodology) is a comprehensive, professional software testing framework adaptable to various software development methodologies including Agile, Scrum, and Waterfall.

## 🎯 Overview

This framework provides a structured approach to software testing through six core phases, with detailed guidance for implementing testing practices across different project methodologies. It serves as both a knowledge base for testing professionals and a foundation for building multi-platform testing management applications.

## 📚 Documentation

### [Complete Documentation →](docs/README.md)

## 🔄 Six Phases of Software Testing

1. **[Test Planning](docs/phases/01-test-planning.md)** - Define scope, strategy, resources, and timelines
2. **[Test Case Development](docs/phases/02-test-case-development.md)** - Design and document test scenarios and cases
3. **[Test Environment Preparation](docs/phases/03-test-environment-preparation.md)** - Set up infrastructure and tools
4. **[Test Execution](docs/phases/04-test-execution.md)** - Execute tests and manage defects
5. **[Test Results Analysis](docs/phases/05-test-results-analysis.md)** - Analyze outcomes and identify patterns
6. **[Test Results Reporting](docs/phases/06-test-results-reporting.md)** - Communicate findings to stakeholders

## 🔧 Methodology Guides

- **[Agile Testing](docs/methodologies/agile.md)** - Continuous testing with rapid feedback
- **[Scrum Testing](docs/methodologies/scrum.md)** - Sprint-based testing approach
- **[Waterfall Testing](docs/methodologies/waterfall.md)** - Sequential phase-based testing
- **[Methodology Comparison](docs/methodologies/comparison.md)** - Detailed comparison and selection guide

## 📋 Templates & Resources

- **[Templates](docs/templates/README.md)** - Ready-to-use templates for test plans, test cases, and reports
- **[Examples](docs/examples/README.md)** - Practical examples and sample artifacts
- **[Multi-Platform App Guide](docs/integration/multi-platform-guide.md)** - Build testing management applications

## 🚀 Key Features

- ✅ **Methodology Agnostic** - Adaptable to Agile, Scrum, Waterfall, and hybrid approaches
- ✅ **Comprehensive Coverage** - End-to-end testing process from planning to reporting
- ✅ **Professional Standards** - Industry best practices and quality standards
- ✅ **Practical Templates** - Ready-to-use templates for immediate implementation
- ✅ **Scalable** - Suitable for projects of all sizes
- ✅ **App-Ready** - Foundation for building testing management tools

## 💡 Use Cases

### For Testing Teams
- Implement structured testing processes
- Improve test coverage and quality
- Standardize testing practices
- Reduce defects and improve software quality

### For Project Managers
- Plan testing activities and resources
- Track testing progress and metrics
- Manage testing risks
- Ensure quality standards

### For Organizations
- Establish testing standards
- Train testing teams
- Improve testing maturity
- Build custom testing tools

### For Developers
- Build multi-platform testing management applications
- Integrate testing into development workflows
- Automate testing processes
- Create testing dashboards and reports

## 🛠️ Building a Multi-Platform App

This framework can serve as the foundation for building comprehensive testing management applications. See our [Multi-Platform App Integration Guide](docs/integration/multi-platform-guide.md) for:

- Recommended technology stacks
- Application architecture
- Core features and modules
- API design
- Development roadmap
- Implementation considerations

## 📖 Quick Start

### New to BGSTM? 
👉 **[Start Here: Getting Started Guide](docs/GETTING-STARTED.md)** - Complete walkthrough for beginners

### Quick Reference:
1. **Choose Your Methodology**: Review [methodology guides](docs/methodologies/comparison.md) to select the best approach
2. **Understand the Phases**: Read through the [six testing phases](docs/phases/01-test-planning.md)
3. **Use Templates**: Download and customize [templates](docs/templates/README.md) for your project
4. **Implement**: Apply the framework to your testing processes
5. **Build (Optional)**: Use as foundation for custom testing tools

## 🚀 Running the Application

### Frontend + Backend (Docker Compose - Recommended)

The easiest way to run the complete application is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/bg-playground/BGSTM.git
cd BGSTM

# Copy environment file
cp .env.example .env

# Start all services (database, backend, frontend)
docker-compose up -d

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Frontend Development

To run the frontend locally for development:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Access at http://localhost:3000
```

### Backend Development

To run the backend locally:

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database (PostgreSQL)
# Update DATABASE_URL in .env file

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

## 🤝 Contributing

Contributions are welcome! Whether you want to:
- Improve documentation
- Add examples
- Share templates
- Report issues
- Suggest features

Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on how to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Resources

- [ISTQB (International Software Testing Qualifications Board)](https://www.istqb.org/)
- [Agile Testing by Lisa Crispin and Janet Gregory](https://agiletester.ca/)
- [Test Automation Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

## 📞 Support

For questions, suggestions, or discussions, please open an issue in this repository.

---

**Made with ❤️ for the software testing community**
