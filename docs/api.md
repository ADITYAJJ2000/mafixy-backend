# Mafixy API Documentation

## Overview
Mafixy is an AI-powered facial analysis and improvement platform API. It provides endpoints for user management, facial analysis, progress tracking, and premium features.

## Base URL
`http://localhost:8000/api`

## Authentication
All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## API Endpoints

### 1. Authentication

#### POST /auth/register
Register a new user.

Request Body:
```json
{
    "email": "user@example.com",
    "password": "secure_password",
    "full_name": "John Doe",
    "age": 25,
    "gender": "male",
    "height": 175.0,
    "weight": 70.0
}
```

Response:
```json
{
    "id": "user_123",
    "email": "user@example.com",
    "full_name": "John Doe"
}
```

#### POST /auth/login
Authenticate user and get JWT token.

Request Body:
```json
{
    "email": "user@example.com",
    "password": "secure_password"
}
```

Response:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### 2. User Management

#### GET /user/profile
Get user profile information.

Response:
```json
{
    "id": "user_123",
    "full_name": "John Doe",
    "age": 25,
    "gender": "male",
    "height": 175.0,
    "weight": 70.0,
    "goals": ["improve_symmetry", "strengthen_jawline"],
    "is_premium": false
}
```

#### PUT /user/profile
Update user profile.

Request Body:
```json
{
    "full_name": "John Smith",
    "age": 26,
    "goals": ["improve_symmetry", "enhance_facial_ratio"]
}
```

### 3. Facial Analysis

#### POST /analyze
Analyze facial features from an image.

Request Body:
```json
{
    "image": "base64_encoded_image_string",
    "type": "photo"
}
```

Response:
```json
{
    "id": "analysis_123",
    "scores": {
        "symmetry": 85.0,
        "jawline": 78.0,
        "facial_ratio": 92.0,
        "skin_clarity": 85.0,
        "overall": 84.5
    },
    "improvement_tips": [
        "Practice facial symmetry exercises",
        "Strengthen jawline muscles"
    ],
    "exercise_recommendations": [
        {
            "exercise_id": "ex_123",
            "name": "Facial Symmetry Exercise",
            "priority": 1
        }
    ]
}
```

### 4. Analysis History

#### GET /history
Get user's analysis history.

Response:
```json
[
    {
        "id": "analysis_123",
        "scores": {
            "symmetry": 85.0,
            "jawline": 78.0,
            "facial_ratio": 92.0,
            "skin_clarity": 85.0
        },
        "timestamp": "2025-07-26T13:28:50.123456",
        "exercise_recommendations": [...]
    }
]
```

### 5. Exercise Management

#### GET /exercises
Get available exercises.

Response:
```json
[
    {
        "id": "ex_123",
        "name": "Facial Symmetry Exercise",
        "category": "symmetry",
        "difficulty": "medium",
        "duration": 5,
        "video_url": "https://example.com/exercises/ex_123.mp4"
    }
]
```

#### POST /exercises/history
Record exercise completion.

Request Body:
```json
{
    "exercise_id": "ex_123",
    "duration_seconds": 300,
    "success_rate": 0.85,
    "notes": "Completed successfully"
}
```

### 6. Premium Features

#### GET /premium/status
Check premium status.

Response:
```json
{
    "is_premium": false,
    "expires_at": "2025-08-26T13:28:50.123456",
    "features": [
        "unlimited_analyses",
        "advanced_analytics",
        "custom_plans"
    ]
}
```

#### POST /premium/subscribe
Subscribe to premium.

Request Body:
```json
{
    "payment_method": "stripe",
    "plan_id": "premium_monthly"
}
```

### 7. WebSocket Real-time Updates

#### Connection
Connect to WebSocket endpoint:
```
ws://localhost:8000/ws
```

#### Events
- `analysis_update`: New analysis results
- `exercise_update`: Exercise completion status
- `achievement_unlocked`: New achievement unlocked

### Error Responses

All endpoints may return error responses in the following format:
```json
{
    "detail": "Error message describing what went wrong",
    "error_type": "validation|authentication|server"
}
```

## WebSocket Events

### 1. Connection Events
- `connect`: Client connects to WebSocket
- `disconnect`: Client disconnects

### 2. Data Events
- `analysis_update`: New analysis results
- `exercise_update`: Exercise completion status
- `achievement_unlocked`: New achievement unlocked

## Security

### Authentication
- JWT-based authentication
- Role-based access control
- Rate limiting
- Input validation
- CORS configuration

### Data Protection
- Sensitive data encryption
- Secure file storage
- Regular security audits

## Integration Points

### 1. Frontend Integration
- REST API endpoints
- WebSocket connections
- Authentication flow
- Error handling

### 2. Third-party Services
- Payment gateways
- Email providers
- Storage services

## Best Practices

1. Always validate input data
2. Handle errors gracefully
3. Use proper authentication
4. Implement rate limiting
5. Follow REST principles
6. Use WebSocket for real-time updates
7. Document all endpoints
8. Implement proper error handling
9. Use proper HTTP status codes
10. Follow security best practices
