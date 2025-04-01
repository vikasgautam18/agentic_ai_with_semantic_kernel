# Agentic AI with Semantic Kernel

This project demonstrates the use of Semantic Kernel to build intelligent systems capable of processing and reasoning over structured and unstructured data. It includes various demos, plugins, and resources to showcase the capabilities of agentic AI.

## Project Structure

### Key Directories

- **resources/**: Contains setup scripts and transcripts for initializing and testing the project.
  - `setup/`: Includes scripts like `setup_db.sql` and `setup.sh` for database and environment setup.
  - `transcripts/`: Stores example transcripts for testing and analysis.

- **src/**: Main source code and demos for the project.
  - `demos/`: Jupyter notebooks demonstrating various use cases of Semantic Kernel, such as group chat analysis and SQL database interactions.
  - `plugins/`: Contains prompt templates for specific functionalities, such as handling blocked cards and reasons.

## Getting Started

1. **Setup Environment**:
   - Use the scripts in `resources/setup/` to initialize the database and environment.
   - Example:
     ```bash
     bash resources/setup/setup.sh
     ```

2. **Install Dependencies**:
   - Navigate to the `src/demos/` directory and install the required Python packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **Run Demos**:
   - Open any Jupyter notebook in `src/demos/` to explore the project capabilities.
   - Example:
     ```bash
     jupyter notebook src/demos/TestGroupChat.ipynb
     ```

## Features

- **Group Chat Analysis**: Analyze group chat data using Semantic Kernel.
- **SQL Database Interaction**: Demonstrates advanced SQL database operations.
- **Prompt Engineering**: Includes templates for handling specific scenarios like blocked cards.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## Contact

For questions or support, please refer to the [transcripts](resources/transcripts/) or contact the project maintainers.

