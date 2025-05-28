# OnArrival Security Features

## Overview

This document outlines the comprehensive security features implemented in the OnArrival application to protect against common web application vulnerabilities and ensure safe operation.

## 🔒 Security Features Implemented

### 1. Input Validation & Sanitization

#### Phone Number Validation
- **E.164 Format**: All phone numbers are validated against the international E.164 standard
- **Multiple Formats**: Supports various input formats (US domestic, international, with/without country codes)
- **Sanitization**: Phone numbers are normalized to a consistent format

#### Message Content Validation
- **Length Limits**: Messages are limited to 1600 characters to prevent abuse
- **Content Sanitization**: HTML entities are escaped to prevent injection
- **Special Character Handling**: Dangerous characters are removed or escaped
- **SSML Protection**: Prevents Speech Synthesis Markup Language injection in TTS

#### Name & Business Name Validation
- **Character Restrictions**: Only allow safe characters (letters, numbers, common punctuation)
- **Length Limits**: Enforce reasonable length limits (50-100 characters)
- **Unicode Normalization**: Handles international characters safely

### 2. API Authentication & Authorization

#### API Key Authentication
- **Secure Key Generation**: Uses cryptographically secure random key generation
- **Permission-Based Access**: Different API keys can have different permissions
- **Environment-Specific Keys**: Separate keys for development and production

#### Session Management
- **JWT Tokens**: Secure session tokens with expiration
- **CSRF Protection**: Cross-Site Request Forgery protection for web forms
- **Session Timeout**: Configurable session timeouts (default: 30 minutes)

### 3. Rate Limiting

#### Endpoint-Specific Limits
- **Authentication**: 20 attempts per hour per IP
- **API Calls**: 100 requests per hour per API key
- **Alert Sending**: 50 alerts per hour per API key

#### IP-Based Protection
- **Failed Attempt Tracking**: Tracks failed authentication attempts
- **Lockout Protection**: Temporary IP lockouts after repeated failures
- **Rate Window Management**: Sliding window rate limiting

### 4. Request Validation

#### Size Limits
- **Request Payload**: Maximum 50KB per request
- **Content Validation**: Validates JSON structure and content
- **Parameter Sanitization**: URL parameters are properly decoded and validated

#### URL Validation
- **Webhook Security**: Validates webhook URLs before making calls
- **Protocol Restrictions**: Only allows safe protocols (HTTP/HTTPS)
- **Domain Validation**: Prevents SSRF attacks

### 5. TwiML Security

#### Speech Synthesis Protection
- **Content Sanitization**: Removes dangerous markup from TTS content
- **Length Limits**: Prevents extremely long speeches
- **Character Filtering**: Removes control characters that might affect TTS
- **SSML Injection Prevention**: Strips SSML tags to prevent voice manipulation

### 6. Data Integrity

#### Storage Validation
- **Data Consistency**: Validates data integrity on startup
- **Duplicate Prevention**: Prevents duplicate contacts and groups
- **Corruption Recovery**: Attempts to repair corrupted data automatically

#### Contact Management
- **Unique Constraints**: Enforces unique phone numbers and names
- **Group Validation**: Validates group membership and prevents orphaned contacts
- **Safe Deletion**: Removes contacts from all groups when deleted

## 🛡️ Security Headers

The application sets the following security headers:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'
```

## 🔧 Configuration

### Environment Variables

```bash
# Security Configuration
SECRET_KEY=your_secret_key_minimum_32_characters_long
API_KEY_DEVELOPMENT=dev_api_key_change_in_production
API_KEY_PRODUCTION=prod_api_key_minimum_32_characters_long

# Session Configuration
SESSION_TIMEOUT_MINUTES=30

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:*,http://127.0.0.1:*

# Environment
ENVIRONMENT=development  # or 'production'
```

### Production Recommendations

1. **Use Strong API Keys**: Generate cryptographically secure API keys (minimum 32 characters)
2. **Set Secure SECRET_KEY**: Use a strong, random secret key for session management
3. **Configure CORS Properly**: Restrict CORS origins to your actual domains
4. **Use HTTPS**: Always use HTTPS in production
5. **Monitor Logs**: Set up monitoring for security events
6. **Regular Updates**: Keep dependencies updated

## 📋 API Usage

### Authentication

All API endpoints require authentication via API key:

```bash
# Header-based authentication (recommended)
curl -H "X-API-Key: your_api_key_here" \
     -H "Content-Type: application/json" \
     https://your-domain.com/api/send_business

# Parameter-based authentication
curl -X POST "https://your-domain.com/api/send_business?api_key=your_api_key_here"
```

### Error Responses

The API returns structured error responses:

```json
{
  "success": false,
  "error": "Validation error message",
  "details": ["Additional error details"]
}
```

## 🚨 Security Events

The application logs the following security events:

- Failed authentication attempts
- Rate limit violations
- Input validation failures
- Suspicious request patterns
- TwiML generation errors

## 🔍 Vulnerability Assessment

### Protections Against Common Attacks

- **SQL Injection**: N/A (using JSON file storage)
- **XSS**: Input sanitization and output encoding
- **CSRF**: CSRF tokens for web forms
- **SSRF**: URL validation for webhooks
- **Injection**: Content sanitization for TTS
- **Rate Limiting**: Protection against DoS attacks
- **Authentication Bypass**: Strong API key validation

### Known Limitations

1. **File-based Storage**: Not suitable for high-scale deployments
2. **Memory-based Rate Limiting**: Rate limits reset on application restart
3. **Single Instance**: No distributed session management

## 📞 Reporting Security Issues

If you discover a security vulnerability, please:

1. **Do NOT** open a public GitHub issue
2. Contact the maintainers privately
3. Provide detailed information about the vulnerability
4. Allow time for the issue to be resolved before public disclosure

## 🔄 Security Maintenance

### Regular Tasks

- Review and rotate API keys quarterly
- Monitor failed authentication attempts
- Update dependencies regularly
- Review security logs weekly
- Test backup and recovery procedures

### Security Audits

Recommended security review areas:

- Input validation effectiveness
- Authentication bypass attempts
- Rate limiting configuration
- TwiML content sanitization
- API endpoint security
- Error message information disclosure 