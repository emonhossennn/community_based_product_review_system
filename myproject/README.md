# Community-Based Product Review System API

A Django REST Framework API for managing product reviews with admin approval workflow.

## Features

- **Product Management**: Create and view products
- **Comment System**: Users can post comments about products
- **Admin Approval**: Comments require admin approval before being publicly visible
- **Authentication**: Token-based authentication for secure access
- **Admin Interface**: Full Django admin interface for managing products and comments

## Setup

1. Install dependencies:
```bash
pip install djangorestframework
```

2. Run migrations:
```bash
python manage.py makemigrations myproject
python manage.py migrate
```

3. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

4. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- **Token Authentication**: Use `Authorization: Token <your_token>` header
- **Session Authentication**: Available for browser-based testing

### Products

#### List Products
```
GET /api/products/
```
Returns all products (public access)

#### Get Product Details
```
GET /api/products/{id}/
```
Returns specific product details

#### Get Product Comments
```
GET /api/products/{id}/comments/
```
Returns all **approved** comments for a specific product

### Comments

#### Create Comment (Authenticated Users Only)
```
POST /api/comments/
Content-Type: application/json
Authorization: Token <your_token>

{
    "product": 1,
    "content": "This is a great product!"
}
```

#### List User's Comments
```
GET /api/comments/
Authorization: Token <your_token>
```
- Regular users: See only their own comments
- Admin users: See all comments

#### Get Comment Details
```
GET /api/comments/{id}/
Authorization: Token <your_token>
```

#### Update Comment
```
PUT /api/comments/{id}/
Authorization: Token <your_token>
```

#### Delete Comment
```
DELETE /api/comments/{id}/
Authorization: Token <your_token>
```

### Admin Endpoints (Admin Users Only)

#### Approve Comment
```
PATCH /api/comments/{id}/approve/
Authorization: Token <admin_token>
```

#### Reject Comment
```
PATCH /api/comments/{id}/reject/
Authorization: Token <admin_token>
```

#### Get Pending Comments
```
GET /api/comments/pending/
Authorization: Token <admin_token>
```
Returns all comments awaiting approval

#### Get Approved Comments
```
GET /api/comments/approved/
Authorization: Token <admin_token>
```
Returns all approved comments

## Data Models

### Product
- `id`: Primary key
- `name`: Product name (max 200 characters)
- `description`: Product description (optional)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Comment
- `id`: Primary key
- `product`: Foreign key to Product
- `user`: Foreign key to User (automatically set)
- `content`: Comment text
- `is_approved`: Boolean flag for approval status
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Response Format

### Comment Response
```json
{
    "id": 1,
    "product": 1,
    "user": 1,
    "username": "john_doe",
    "content": "This is a great product!",
    "is_approved": true,
    "created_at": "2024-01-15T10:30:00Z",
    "time_ago": "2 days ago"
}
```

### Product Response
```json
{
    "id": 1,
    "name": "iPhone 16",
    "description": "Latest iPhone model",
    "created_at": "2024-01-10T09:00:00Z",
    "updated_at": "2024-01-10T09:00:00Z"
}
```

## Admin Interface

Access the Django admin interface at `/admin/` to:
- Manage products
- Review and approve/reject comments
- View user information
- Bulk approve/reject comments

## Usage Examples

### 1. Create a Product (via Admin)
Use the Django admin interface or create via API (if you add write permissions)

### 2. Post a Comment
```bash
curl -X POST http://localhost:8000/api/comments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token <your_token>" \
  -d '{"product": 1, "content": "Amazing product!"}'
```

### 3. Get Approved Comments for a Product
```bash
curl http://localhost:8000/api/products/1/comments/
```

### 4. Admin Approves a Comment
```bash
curl -X PATCH http://localhost:8000/api/comments/1/approve/ \
  -H "Authorization: Token <admin_token>"
```

## Security Features

- **Authentication Required**: All comment operations require authentication
- **Admin-Only Actions**: Approval/rejection actions restricted to admin users
- **User Isolation**: Regular users can only see their own comments
- **Approval Workflow**: Comments are not publicly visible until approved

## Testing

1. Start the server: `python manage.py runserver`
2. Visit `http://localhost:8000/admin/` to access admin interface
3. Use tools like Postman or curl to test API endpoints
4. Visit `http://localhost:8000/api/` to see available endpoints 