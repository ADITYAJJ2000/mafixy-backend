# Mafixy Backend

Mafixy is an AI-powered facial analysis and improvement platform. This repository contains the backend service for the Mafixy application.

## Features

- User authentication and management
- AI-powered facial analysis
- Progress tracking and history
- Exercise management and recommendations
- Premium features and subscription management
- Real-time updates via WebSocket
- Secure file storage and handling

## Tech Stack

- **Backend**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Authentication**: JWT
- **Real-time**: WebSocket
- **AI**: MediaPipe, OpenCV
- **Storage**: AWS S3
- **Testing**: Pytest

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Node.js (for frontend)
- Docker (optional)

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
5. Initialize database:
   ```bash
   python -m alembic upgrade head
   ```

## Running the Application

1. Start the PostgreSQL database
2. Run the application:
   ```bash
   uvicorn main:app --reload
   ```
3. The application will be available at `http://localhost:8000`

## API Documentation

The API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests using pytest:
```bash
pytest tests/
```

## Security

- JWT-based authentication
- Role-based access control
- Input validation
- Rate limiting
- Secure file handling
- Regular security audits

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
