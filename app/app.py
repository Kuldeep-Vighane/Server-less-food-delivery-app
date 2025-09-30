import json
import uuid
import boto3
from datetime import datetime
from urllib.parse import parse_qs
from decimal import Decimal  # ADD THIS IMPORT

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = 'FoodOrders'

# Menu items with fixed prices (keep as float for calculations)
MENU_ITEMS = {
    'pizza': 12.99,
    'burger': 8.99,
    'pasta': 10.99,
    'salad': 7.99,
    'soda': 1.99
}

def handler(event, context):
    """Main Lambda handler function"""
    
    # Extract HTTP method and path
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    path_parameters = event.get('pathParameters', {})
    query_string_parameters = event.get('queryStringParameters', {})
    
    # Parse body if present
    body = {}
    if event.get('body'):
        try:
            if event.get('isBase64Encoded', False):
                import base64
                body_str = base64.b64decode(event['body']).decode('utf-8')
            else:
                body_str = event['body']
            
            if event.get('headers', {}).get('content-type', '').startswith('application/json'):
                body = json.loads(body_str)
            else:
                body = parse_qs(body_str)
                # Flatten the parsed form data
                body = {k: v[0] if len(v) == 1 else v for k, v in body.items()}
        except:
            body = {}
    
    # Route the request
    if path == '/' and http_method == 'GET':
        return landing_page()
    elif path == '/purchase' and http_method == 'GET':
        return purchase_page()
    elif path == '/order' and http_method == 'POST':
        return create_order(body)
    elif path.startswith('/track/') and http_method == 'GET':
        order_id = path_parameters.get('order_id') or path.split('/')[-1]
        return track_order(order_id)
    elif path.startswith('/order/') and path.endswith('/cancel') and http_method == 'PUT':
        order_id = path_parameters.get('order_id') or path.split('/')[-2]
        return cancel_order(order_id)
    else:
        return error_response('Page not found', 404)

def landing_page():
    """Landing page with welcome message and navigation"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Food Delivery Service</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 600px; margin: 0 auto; }
            .button { display: inline-block; padding: 10px 20px; margin: 10px; 
                     background: #007bff; color: white; text-decoration: none; 
                     border-radius: 5px; }
            .button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Food Delivery Service</h1>
            <p>Order delicious food and track your delivery in real-time!</p>
            <div>
                <a href="/purchase" class="button">Place New Order</a>
                <a href="/track" class="button">Track Existing Order</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html_response(html)

def purchase_page():
    """Purchase page with order form"""
    menu_options = ""
    for item, price in MENU_ITEMS.items():
        menu_options += f'<label><input type="checkbox" name="items" value="{item}"> {item.title()} - ${price:.2f}</label><br>'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Place Your Order</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .container {{ max-width: 600px; margin: 0 auto; }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; margin-bottom: 5px; }}
            input[type="text"], input[type="email"] {{ width: 100%; padding: 8px; }}
            .button {{ padding: 10px 20px; background: #28a745; color: white; 
                     border: none; border-radius: 5px; cursor: pointer; }}
            .button:hover {{ background: #218838; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Place Your Order</h1>
            <form action="/order" method="POST">
                <div class="form-group">
                    <label for="customer_name">Customer Name:</label>
                    <input type="text" id="customer_name" name="customer_name" required>
                </div>
                <div class="form-group">
                    <label for="customer_email">Customer Email:</label>
                    <input type="email" id="customer_email" name="customer_email" required>
                </div>
                <div class="form-group">
                    <label>Food Items:</label>
                    {menu_options}
                </div>
                <button type="submit" class="button">Submit Order</button>
            </form>
            <p><a href="/">← Back to Home</a></p>
        </div>
    </body>
    </html>
    """
    return html_response(html)

def create_order(body):
    """Create a new order"""
    try:
        customer_name = body.get('customer_name', '').strip()
        customer_email = body.get('customer_email', '').strip()
        items = body.get('items', [])
        
        if not customer_name or not customer_email:
            return error_response('Customer name and email are required')
        
        if isinstance(items, str):
            items = [items]
        
        if not items:
            return error_response('Please select at least one item')
        
        # Calculate total and format items - FIXED FOR DYNAMODB
        order_items = []
        total = Decimal('0.0')  # Use Decimal instead of float
        for item in items:
            if item in MENU_ITEMS:
                # Convert price to Decimal for DynamoDB
                item_price = Decimal(str(MENU_ITEMS[item]))
                order_items.append({
                    'name': item,
                    'price': item_price  # Use Decimal instead of float
                })
                total += item_price
        
        # Generate order details
        order_id = str(uuid.uuid4())
        current_time = datetime.utcnow().isoformat()
        
        order = {
            'order_id': order_id,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'items': order_items,
            'total': total,  # This is now a Decimal
            'status': 'Received',
            'created_at': current_time,
            'updated_at': current_time
        }
        
        # Save to DynamoDB
        table = dynamodb.Table(table_name)
        table.put_item(Item=order)
        
        # Convert total back to float for display
        total_display = float(total)
        
        # Return confirmation page
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Order Confirmation</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .success {{ color: #28a745; }}
                .button {{ display: inline-block; padding: 10px 20px; margin: 10px; 
                         background: #007bff; color: white; text-decoration: none; 
                         border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="success">Thank You!</h1>
                <p>Your order has been placed successfully.</p>
                <p><strong>Order ID:</strong> {order_id}</p>
                <p><strong>Total Amount:</strong> ${total_display:.2f}</p>
                <div>
                    <a href="/track/{order_id}" class="button">Track Your Order</a>
                    <a href="/" class="button">Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html_response(html)
        
    except Exception as e:
        return error_response(f'Error creating order: {str(e)}')

def track_order(order_id):
    """Track an existing order"""
    try:
        if not order_id:
            # Show tracking input page
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Track Your Order</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 600px; margin: 0 auto; }
                    .form-group { margin-bottom: 15px; }
                    label { display: block; margin-bottom: 5px; }
                    input[type="text"] { width: 100%; padding: 8px; }
                    .button { padding: 10px 20px; background: #007bff; color: white; 
                             border: none; border-radius: 5px; cursor: pointer; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Track Your Order</h1>
                    <form action="/track" method="GET">
                        <div class="form-group">
                            <label for="order_id">Enter your Order ID:</label>
                            <input type="text" id="order_id" name="order_id" required>
                        </div>
                        <button type="submit" class="button">Track Order</button>
                    </form>
                    <p><a href="/">← Back to Home</a></p>
                </div>
            </body>
            </html>
            """
            return html_response(html)
        
        # Fetch order from DynamoDB
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={'order_id': order_id})
        
        if 'Item' not in response:
            return error_response('Order not found. Please check your Order ID.')
        
        order = response['Item']
        
        # Format items for display - handle Decimal values
        items_html = ""
        for item in order.get('items', []):
            # Convert Decimal to float for display
            price = float(item.get('price', Decimal('0.0')))
            items_html += f"<li>{item.get('name', '').title()} - ${price:.2f}</li>"
        
        # Convert total to float for display
        total_display = float(order.get('total', Decimal('0.0')))
        
        # Cancel button logic
        cancel_button = ""
        if order.get('status') not in ['Delivered', 'Cancelled']:
            cancel_button = f"""
            <form action="/order/{order_id}/cancel" method="POST" style="margin-top: 20px;">
                <button type="submit" class="button cancel">Cancel Order</button>
            </form>
            <script>
                document.querySelector('form').addEventListener('submit', function(e) {{
                    e.preventDefault();
                    if(confirm('Are you sure you want to cancel this order?')) {{
                        fetch('/order/{order_id}/cancel', {{ method: 'PUT' }})
                            .then(response => response.json())
                            .then(data => {{
                                alert(data.message);
                                window.location.reload();
                            }});
                    }}
                }});
            </script>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Order Tracking</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .order-details {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .button {{ padding: 10px 20px; background: #007bff; color: white; 
                         text-decoration: none; border-radius: 5px; display: inline-block; }}
                .button.cancel {{ background: #dc3545; }}
                .button.cancel:hover {{ background: #c82333; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Order Tracking</h1>
                <div class="order-details">
                    <p><strong>Order ID:</strong> {order.get('order_id')}</p>
                    <p><strong>Customer Name:</strong> {order.get('customer_name')}</p>
                    <p><strong>Status:</strong> {order.get('status')}</p>
                    <p><strong>Items:</strong></p>
                    <ul>{items_html}</ul>
                    <p><strong>Total:</strong> ${total_display:.2f}</p>
                    <p><strong>Order Created:</strong> {format_timestamp(order.get('created_at'))}</p>
                    <p><strong>Last Updated:</strong> {format_timestamp(order.get('updated_at'))}</p>
                </div>
                {cancel_button}
                <p style="margin-top: 20px;"><a href="/" class="button">Back to Home</a></p>
            </div>
        </body>
        </html>
        """
        return html_response(html)
        
    except Exception as e:
        return error_response(f'Error tracking order: {str(e)}')

def cancel_order(order_id):
    """Cancel an order"""
    try:
        if not order_id:
            return error_response('Order ID is required')
        
        # Fetch order from DynamoDB
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={'order_id': order_id})
        
        if 'Item' not in response:
            return error_response('Order not found')
        
        order = response['Item']
        current_status = order.get('status')
        
        if current_status in ['Delivered', 'Cancelled']:
            return json_response({
                'message': f'This order can no longer be cancelled. Current status: {current_status}'
            }, 400)
        
        # Update order status
        current_time = datetime.utcnow().isoformat()
        table.update_item(
            Key={'order_id': order_id},
            UpdateExpression='SET #status = :status, #updated_at = :updated_at',
            ExpressionAttributeNames={
                '#status': 'status',
                '#updated_at': 'updated_at'
            },
            ExpressionAttributeValues={
                ':status': 'Cancelled',
                ':updated_at': current_time
            }
        )
        
        return json_response({'message': 'Your order has been successfully cancelled.'})
        
    except Exception as e:
        return error_response(f'Error cancelling order: {str(e)}')

def format_timestamp(timestamp):
    """Format ISO timestamp for display"""
    if not timestamp:
        return 'N/A'
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp

def html_response(html, status_code=200):
    """Return HTML response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'text/html'
        },
        'body': html
    }

def json_response(data, status_code=200):
    """Return JSON response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(data, default=decimal_default)  # ADDED custom serializer
    }

def decimal_default(obj):
    """Custom JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def error_response(message, status_code=400):
    """Return error response"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .error {{ color: #dc3545; }}
        </style>
    </head>
    <body>
        <div class="error">
            <h1>Error</h1>
            <p>{message}</p>
            <p><a href="/">← Back to Home</a></p>
        </div>
    </body>
    </html>
    """
    return html_response(html, status_code)
