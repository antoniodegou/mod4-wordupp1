import stripe
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Create a product
product = stripe.Product.create(name='Subscription')

# Create free plan
free_plan = stripe.Plan.create(
  currency='usd',
  interval='month',
  product=product['id'],
  nickname='Free Plan',
  amount=0,
  id='free'
)

# Create premium plan
premium_plan = stripe.Plan.create(
  currency='usd',
  interval='month',
  product=product['id'],
  nickname='Premium Plan',
  amount=199,  # $1.99
  id='premium'
)

print(f"Product ID: {product['id']}")
print(f"Free Plan ID: {free_plan['id']}")
print(f"Premium Plan ID: {premium_plan['id']}")
