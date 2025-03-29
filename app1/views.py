from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from app1.models import reg_form_ch, login, reg_form_us, foodpost,Review,Orders,Report
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import check_password
import datetime
from django.contrib import messages
from django.conf import settings
import razorpay

def home(request):
    template = loader.get_template("home.html")
    context = {}
    return HttpResponse(template.render(context, request))

def userhm(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    foods = foodpost.objects.all()

    if query:
        foods = foods.filter(title__icontains=query) | foods.filter(chef__name__icontains=query)

    if category:
        foods = foods.filter(category=category)

    return render(request, 'userhm.html', {'foods': foods})

def Login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')  # Ensure the form field matches this name

        try:
            l = login.objects.get(username=username)  # Fetch by username only

            if l.passw == password:  # Compare passwords
                request.session["login_id"] = l.id  
                request.session["uid"] = l.object_id  
                request.session["user_type"] = l.utype  

                if l.utype == 'chef':
                    return HttpResponse("<script>alert('WELCOME CHEF');window.location='/chefhm';</script>")
                elif l.utype == 'user':
                    return HttpResponse("<script>alert('WELCOME USER');window.location='/userhm';</script>")
                elif l.utype == 'admin':  # Check if the user is an admin
                    return HttpResponse("<script>alert('WELCOME ADMIN');window.location='/admin_home';</script>")
                else:
                    return HttpResponse("<script>alert('Invalid User Type');window.location='/login';</script>")
            else:
                return HttpResponse("<script>alert('Invalid Password');window.location='/login';</script>")

        except login.DoesNotExist:
            return HttpResponse("<script>alert('Invalid Username');window.location='/login';</script>")

    return render(request, "home.html")

def reg_form_user(request):
    if request.method == 'POST':
        r = reg_form_us.objects.create(
            name=request.POST.get('name'),
            gender=request.POST.get('gender'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            image=request.FILES.get('image'),
            address=request.POST.get('address'),
            location=request.POST.get('location'),
        )

        l = login.objects.create(
            username=request.POST.get("username"),
            passw=request.POST.get("password"),
            content_type=ContentType.objects.get_for_model(reg_form_us),
            object_id=r.id,
            utype='user'
        )

        return HttpResponse("<script>alert('Registration Successful');window.location='/login';</script>")
    else:
        template = loader.get_template("reg_form_user.html")
        return HttpResponse(template.render({}, request))

def reg_form_chef(request):
    if request.method == 'POST':
        r = reg_form_ch.objects.create(
            name=request.POST.get('name'),
            gender=request.POST.get('gender'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            image=request.FILES.get('image'),
            id_card=request.FILES.get('id_card'),
            location=request.POST.get('location'),
            address=request.POST.get('address'),
            accnum=request.POST.get('accnum'),
            ifsc=request.POST.get('ifsc')
        )
        l = login.objects.create(
            username=request.POST.get("username"),
            passw=request.POST.get("password"),
            content_type=ContentType.objects.get_for_model(reg_form_ch),
            object_id=r.id,
            utype='chef'
        )

        return HttpResponse("<script>alert('Chef Registration Successful');window.location='/login';</script>")
    else:
        template = loader.get_template("reg_form_chef.html")
        return HttpResponse(template.render({}, request))

def chefhm(request):
    if "login_id" not in request.session or request.session.get("user_type") != "chef":
        return HttpResponse("<script>alert('Access Denied! Please log in as a chef.');window.location='/login';</script>")

    chef_id = request.session.get("uid")
    chef = get_object_or_404(reg_form_ch, id=chef_id)

    # Get ContentType for `reg_form_ch`
    chef_content_type = ContentType.objects.get_for_model(reg_form_ch)

    # Retrieve only food posts made by this chef
    chef_foods = foodpost.objects.filter(content_type=chef_content_type, object_id=chef.id)

    return render(request, 'chefhome.html', {'chef_foods': chef_foods})

from django.urls import reverse  
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from .models import login, reg_form_ch, foodpost

def postfood(request):
    # Ensure user is logged in as a chef
    if "login_id" not in request.session or request.session.get("user_type") != "chef":
        return HttpResponse("<script>alert('Access Denied! Please log in as a chef.');window.location='/login';</script>")

    # Get the logged-in chef using the same logic as `chef_profile`
    chef_id = request.session.get("uid")  
    chef = get_object_or_404(reg_form_ch, id=chef_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        image = request.FILES.get('image')
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        location = request.POST.get('location')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        dining_type = request.POST.get('dine')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        category=request.POST.get('meal')

        # Validate required fields
        if not all([title, desc, image,image1,image2,price, location, quantity, dining_type, latitude, longitude,]):
            messages.error(request, "All fields are required!")
            return redirect('postfood')

        try:
            # Convert fields to appropriate types
            price = float(price)
            quantity = int(quantity)
            latitude = float(latitude)
            longitude = float(longitude)

            # Assign correct content type for chefs
            chef_content_type = ContentType.objects.get_for_model(reg_form_ch)

            # Save food post with the correct chef's `object_id`
            foodpost.objects.create(
                title=title,
                desc=desc,
                image=image,
                image1=image1,
                image2=image2,
                price=price,
                location=location,
                latitude=latitude,
                longitude=longitude,
                category=category,
                quantity=quantity,
                dining_type=dining_type,
                content_type=chef_content_type,
                object_id=chef.id  # Correctly linking to the logged-in chef
            )
            messages.success(request, "Food posted successfully!")
            return redirect('postfood')

        except ValueError:
            messages.error(request, "Invalid price, quantity, latitude, or longitude")
            return redirect('postfood')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('postfood')

    # Fetch only the logged-in chef’s food posts
    chef_foods = foodpost.objects.filter(content_type=ContentType.objects.get_for_model(reg_form_ch), object_id=chef.id)

    return render(request, 'postfood.html', {'chef_foods': chef_foods})
def chef_profile(request):
    if "login_id" not in request.session or request.session.get("user_type") != "chef":
        return HttpResponse("<script>alert('Access Denied! Please log in as a chef.');window.location='/login';</script>")
    chef_id = request.session.get("uid")  
    chef = get_object_or_404(reg_form_ch, id=chef_id)
    return render(request, "chef_profile.html", {"chef": chef})

def user_profile(request):
    if "login_id" not in request.session or request.session.get("user_type") != "user":
        return HttpResponse("<script>alert('Access Denied! Please log in as a user.');window.location='/login';</script>")
    user_id = request.session.get("uid")  
    user = get_object_or_404(reg_form_us, id=user_id)

    return render(request, "user_profile.html", {"user": user})
def edit_chef_profile(request):
    if "login_id" not in request.session or request.session.get("user_type") != "chef":
        return HttpResponse("<script>alert('Access Denied! Please log in as a chef.');window.location='/login';</script>")

    chef_id = request.session.get("uid")
    chef = get_object_or_404(reg_form_ch, id=chef_id)

    # Get the content type for the chef model
    chef_content_type = ContentType.objects.get_for_model(reg_form_ch)

    # Fetch the corresponding login entry
    login_entry = get_object_or_404(login, content_type=chef_content_type, object_id=chef.id, utype="chef")

    if request.method == "POST":
        chef.name = request.POST.get("name")
        chef.phone = request.POST.get("phone")
        chef.email = request.POST.get("email")
        chef.location = request.POST.get("location")
        chef.address = request.POST.get("address")
        chef.accnum = request.POST.get("accnum")
        chef.ifsc = request.POST.get("ifsc")

        if 'image' in request.FILES:
            chef.image = request.FILES['image']
        if 'id_card' in request.FILES:
            chef.id_card = request.FILES['id_card']

        # Update username in login model
        new_username = request.POST.get("username")
        if new_username:
            login_entry.username = new_username
            login_entry.save()

        chef.save()
        return HttpResponse("<script>alert('Profile Updated Successfully!');window.location='/chef-profile';</script>")

    return render(request, "edit_chef_profile.html", {"chef": chef, "login": login_entry})

def edit_user_profile(request):
    if "login_id" not in request.session or request.session.get("user_type") != "user":
        return HttpResponse("<script>alert('Access Denied! Please log in as a user.');window.location='/login';</script>")

    user_id = request.session.get("uid")
    user= get_object_or_404(reg_form_us, id=user_id)

    # Get the content type for the chef model
    chef_content_type = ContentType.objects.get_for_model(reg_form_us)

    # Fetch the corresponding login entry
    login_entry = get_object_or_404(login, content_type=chef_content_type, object_id=user.id, utype="user")

    if request.method == "POST":
        user.name = request.POST.get("name")
        user.phone = request.POST.get("phone")
        user.email = request.POST.get("email")
        user.location = request.POST.get("location")
        user.address = request.POST.get("address")

        if 'image' in request.FILES:
            user.image = request.FILES['image']

        # Update username in login model
        new_username = request.POST.get("username")
        if new_username:
            login_entry.username = new_username
            login_entry.save()

        user.save()
        return HttpResponse("<script>alert('Profile Updated Successfully!');window.location='/user_profile';</script>")

    return render(request, "edit_user_profile.html", {"user": user, "login": login_entry})



def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        login_id = request.session.get("login_id")  # Get current logged-in user ID
        if not login_id:
            return HttpResponse("<script>alert('User not logged in!');window.location='/login';</script>")

        try:
            user = login.objects.get(id=login_id)  # Fetch user from login table

            if user.passw != old_password:  # Compare old password as plain text
                return HttpResponse("<script>alert('Old password is incorrect!');window.location='/change_password';</script>")

            if new_password != confirm_password:  # Check if new passwords match
                return HttpResponse("<script>alert('New passwords do not match!');window.location='/change_password';</script>")

            user.passw = new_password  # Update password
            user.save()

            return HttpResponse("<script>alert('Password changed successfully!');window.location='/login';</script>")

        except login.DoesNotExist:
            return HttpResponse("<script>alert('User not found!');window.location='/login';</script>")

    return render(request, "change_chef_password.html")

def change_user_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        login_id = request.session.get("login_id")  # Get current logged-in user ID
        if not login_id:
            return HttpResponse("<script>alert('User not logged in!');window.location='/login';</script>")

        try:
            user = login.objects.get(id=login_id)  # Fetch user from login table

            if user.passw != old_password:  # Compare old password as plain text
                return HttpResponse("<script>alert('Old password is incorrect!');window.location='/change_user_password';</script>")

            if new_password != confirm_password:  # Check if new passwords match
                return HttpResponse("<script>alert('New passwords do not match!');window.location='/change_user_password';</script>")

            user.passw = new_password  # Update password
            user.save()

            return HttpResponse("<script>alert('Password changed successfully!');window.location='/login';</script>")

        except login.DoesNotExist:
            return HttpResponse("<script>alert('User not found!');window.location='/login';</script>")

    return render(request, "change_user_password.html")

def edit_food(request, food_id):
    food = get_object_or_404(foodpost, id=food_id)

    if request.method == "POST":
        try:
            # Update food details
            food.title = request.POST.get("title")
            food.desc = request.POST.get("desc")
            food.price = request.POST.get("price")
            food.quantity = request.POST.get("quantity")
            food.dining_type = request.POST.get("dine")
            food.category=request.POST.get("meal") 
            if food.price:
                food.price = float(food.price)
            if food.quantity:
                food.quantity = int(food.quantity) 


            if "image" in request.FILES:
                food.image = request.FILES["image"]

            food.save()
            messages.success(request, "Food edited successfully!")
            return redirect('chefhome')

        except ValueError:
            messages.error(request, "Invalid price, quantity")
            return redirect('chefhm')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('chefhm')
    
    return render(request, "edit_food.html", {"food": food})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
def delete_food(request, food_id):
    if request.method == "POST":  # Change from DELETE to POST
        food = get_object_or_404(foodpost, id=food_id)
        food.delete()
        return JsonResponse({"success": True, "message": "Food deleted successfully!"})

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400) 

# def food_list(request):
#     query = request.GET.get('q', '')
#     category = request.GET.get('category', '')

#     foods = foodpost.objects.all()

#     if query:
#         foods = foods.filter(title__icontains=query) | foods.filter(chef__name__icontains=query)

#     if category:
#         foods = foods.filter(category=category)

#     return render(request, 'userhm.html', {'foods': foods})

def search_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []

    if query:
        foods = foodpost.objects.filter(title__icontains=query) | foodpost.objects.filter(chef__name__icontains=query)
        suggestions = list(foods.values_list('title', flat=True)) + list(foods.values_list('chef__name', flat=True))

    return JsonResponse({'suggestions': suggestions})  

from django.contrib import messages

def food_details(request, food_id):
    # Fetch the food item and chef
    food = get_object_or_404(foodpost, id=food_id)
    chef = food.chef 
    razorpay_key_id = settings.RAZORPAY_KEY_ID

    # Fetch the logged-in user's ID and type from the session
    uid = request.session.get("uid")
    user_type = request.session.get("user_type")

    # Fetch reviews for the **specific chef**
    reviews_list = Review.objects.filter(
        content_type=ContentType.objects.get_for_model(reg_form_ch),
        object_id=chef.id
    ).select_related('user').order_by('-created_at')

    # Handle POST request for adding a review
    if request.method == "POST":
        if not uid or user_type != "user":
            messages.error(request, "Only users can leave reviews.")
            return redirect('food_details', food_id=food_id)

        rating = request.POST.get("rating")
        comment = request.POST.get("description")  # Ensure correct field name

        if not rating or not comment:
            messages.error(request, "Both rating and comment are required.")
        elif int(rating) < 1 or int(rating) > 5:
            messages.error(request, "Invalid rating. Must be between 1 and 5 stars.")
        else:
            Review.objects.create(
                user=reg_form_us.objects.get(id=uid),  # Fetch user from session ID
                content_type=ContentType.objects.get_for_model(reg_form_ch),
                object_id=chef.id,
                rating=int(rating),
                comment=comment
            )
            messages.success(request, "Review added successfully.")

        return redirect('food_details', food_id=food_id)  # Reload page

    # Fetch the logged-in user if they are a user
    user = None
    if uid and user_type == "user":
        user = reg_form_us.objects.get(id=uid)

    return render(request, "food_details.html", {
        "food": food,
        "chef": chef,
        "reviews": reviews_list,  # Pass reviews to the template
        "user_type": user_type,
        "razorpay_key_id": razorpay_key_id,
        "user": user,
        "amount": food.price,
    })
from django.utils.timezone import now
def place_order(request, food_id):
    if "uid" not in request.session:  # Ensure user is logged in
        return HttpResponse("<script>alert('Please login first!'); window.location='/login';</script>")

    food = get_object_or_404(foodpost, id=food_id)  
    user_id = request.session["uid"]  

    if request.session["user_type"] != "user":
        return HttpResponse("<script>alert('Only users can place orders!'); window.location='/userhm';</script>")

    user = get_object_or_404(reg_form_us, id=user_id)  
    quantity = int(request.POST.get("quantity", 1))
    total_price = food.price * quantity

    order = Orders.objects.create(
        user=user,
        food=food,
        quantity=quantity,
        total_price=total_price,
        chef=food.chef,
        status="Pending",
    )
    return redirect("initiate_payment", order_id=order.id)
def order_page(request):
    if "uid" not in request.session:  # Ensure user is logged in
        return HttpResponse("<script>alert('Please login first!'); window.location='/login';</script>")

    user_id = request.session["uid"]  # Get logged-in user ID
    orders = Orders.objects.filter(user_id=user_id)  

    return render(request, 'order.html', {'orders': orders})

def cancel_order(request, order_id):  # Change to order_id instead of food_id
    if "uid" not in request.session:  # Ensure user is logged in
        return HttpResponse("<script>alert('Please login first!'); window.location='/login';</script>")

    user_id = request.session["uid"]  # Get logged-in user ID

    # Get order by ID, ensure it belongs to the logged-in user
    order = get_object_or_404(Orders, id=order_id, user_id=user_id)
    
    order.delete()  # Delete order from database

    return redirect('order_page')
 
def chef_orders(request):
    if "login_id" not in request.session or request.session.get("user_type") != "chef":
        return HttpResponse("<script>alert('Access Denied! Please log in as a chef.');window.location='/login';</script>")

    object_id = request.session.get("uid")  # This is the object_id from auth table
    
    try:
        chef = reg_form_ch.objects.get(id=object_id)  # Fetch the correct chef instance
    except reg_form_ch.DoesNotExist:
        return HttpResponse("<script>alert('Chef not found!');window.location='/login';</script>")

    # Now filter orders using the actual chef reference
    orders = Orders.objects.filter(chef=chef).select_related("user", "food")

    print("Session object_id:", object_id)
    print("Orders found for chef:", orders)

    return render(request, "chef_orders.html", {"orders": orders})

def update_order_status(request, order_id):
    if request.method == "POST":
        status = request.POST.get("status")  # Get status from form
        order = get_object_or_404(Orders, id=order_id)

        if order.status == "Pending":  # Only update if still pending
            if status in ["Accepted", "Declined"]:  # Ensure only valid statuses
                order.status = status
                order.save()

        return redirect("chef_orders")  # Redirect back to orders page

    return HttpResponse("Invalid request", status=400)




razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def initiate_payment(request, food_id):
    # Fetch the food item and chef
    food = get_object_or_404(foodpost, id=food_id)
    chef = food.chef

    # Fetch the logged-in user
    user_id = request.session.get("uid")
    if not user_id:
        return JsonResponse({"status": "error", "message": "User not logged in!"})

    user = get_object_or_404(reg_form_us, id=user_id)

    # Get quantity (default to 1)
    quantity = int(request.POST.get("quantity", 1))
    total_price = int(food.price * quantity * 100)  # Convert to paise

    # Create a new order
    order = Orders.objects.create(
        user=user,
        food=food,
        quantity=quantity,
        total_price=food.price * quantity,
        chef=chef,
        status="Pending",
    )

    # Create Razorpay order with all payment methods enabled
    razorpay_order = razorpay_client.order.create({
        "amount": total_price,
        "currency": "INR",
        "payment_capture": "1",
        # Ensure no payment method is restricted
    })

    # Store Razorpay order ID in the database
    order.razorpay_order_id = razorpay_order["id"]
    order.save()

    # Return JSON response with all necessary details
    return JsonResponse({
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount": total_price / 100,  # Convert to INR
        "user_name": user.name,
        "user_email": user.email,
        "user_phone": user.phone,
        "food_title": food.title,
        "food_image_url": food.image.url,
        "food_price": str(food.price),
        "food_quantity": quantity,
        "chef_name": chef.name,
        "chef_accnum": chef.accnum,
    })
from django.http import JsonResponse

@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")
        order_id = request.POST.get("razorpay_order_id")
        signature = request.POST.get("razorpay_signature")

        if not payment_id or not order_id or not signature:
            return JsonResponse({"status": "failed", "message": "Missing payment details!"})

        try:
            order = Orders.objects.filter(razorpay_order_id=order_id).first()
            if not order:
                return JsonResponse({"status": "failed", "message": "Order not found!"})

            # Verify the payment signature
            params_dict = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            }

            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:
                order.status = "Failed"
                order.save()
                return JsonResponse({"status": "failed", "message": "Payment verification failed!"})

            # Mark payment as successful
            order.payment_status = True
            order.razorpay_payment_id = payment_id
            order.razorpay_payment_signature = signature
            order.status = "Pending"  # Reset status to Pending for chef to accept/decline
            order.save()

            return JsonResponse({"status": "success", "message": "Payment Successful!"})

        except Exception as e:
            return JsonResponse({"status": "failed", "message": f"Error: {str(e)}"})

    return JsonResponse({"status": "failed", "message": "Invalid request method."})

def chef_reviews(request):
    # Ensure only logged-in chefs can access
    uid = request.session.get("uid")
    user_type = request.session.get("user_type")

    if not uid or user_type != "chef":
        messages.error(request, "You must be logged in as a chef to view reviews.")
        return redirect("chef_login")  # Redirect to chef login

    # Fetch the chef
    chef = get_object_or_404(reg_form_ch, id=uid)

    # Fetch reviews related to this chef
    reviews_list = Review.objects.filter(
        content_type=ContentType.objects.get_for_model(reg_form_ch),
        object_id=chef.id
    ).select_related("user").order_by("-created_at")

    return render(request, "chef_reviews.html", {
        "chef": chef,
        "reviews": reviews_list
    })

def admin_home(request):
    if request.session.get('user_type') != 'admin':
        return redirect('home') 
    
    users = reg_form_us.objects.all()
    chefs = reg_form_ch.objects.all()
    food_posts = foodpost.objects.all()
    reviews = Review.objects.all()
    reports = Report.objects.all()
    
    food_categories = {
        "Breakfast": foodpost.objects.filter(category="Breakfast"),
        "Lunch": foodpost.objects.filter(category="Lunch"),
        "Dinner": foodpost.objects.filter(category="Dinner"),
        "Snack": foodpost.objects.filter(category="Snacks"),
    }

    reviews = Review.objects.all()

    return render(request, "admin_home.html", {
        "users": users,
        "chefs": chefs,
        "food_categories": food_categories,
        "reviews": reviews,
        "reports":reports,
        "food_posts": food_posts,
    })


def delete_user(request, user_id):
    user = get_object_or_404(reg_form_us, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect("admin_home")

def delete_chef(request, chef_id):
    chef = get_object_or_404(reg_form_ch, id=chef_id)
    chef.delete()
    messages.success(request, "Chef deleted successfully.")
    return redirect("admin_home")

def delete_food(request, food_id):
    food = get_object_or_404(foodpost, id=food_id)
    food.delete()
    messages.success(request, "Food post deleted successfully.")
    return redirect("admin_home")

def delete_category(request, category):
    foodpost.objects.filter(category=category).delete()
    messages.success(request, f"All {category} food items deleted successfully.")
    return redirect("admin_home")

def report_to_admin(request):
    if request.method == "POST":
        food_id = request.POST.get("food_id")
        chef_id = request.POST.get("chef_id")
        user_id = request.POST.get("user_id")
        comment = request.POST.get("report_comment")

        try:
            user = reg_form_us.objects.get(id=user_id)
            chef = reg_form_ch.objects.get(id=chef_id)
            food = foodpost.objects.get(id=food_id)

            Report.objects.create(user=user, chef=chef, food=food, comment=comment)

            return redirect("/food_details/" + food_id)  # Redirect back to food details
        except Exception as e:
            return HttpResponse(f"Error: {e}")

    return redirect("/")