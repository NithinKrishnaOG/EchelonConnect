from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from core.models import *
from django.urls import reverse
from itertools import chain


def admin(request):
    if request.user.is_authenticated and request.user.is_staff:
        # Redirect to the admin dashboard if the admin is already authenticated
        return redirect('admin_home.html')  # Update with the admin dashboard URL or view name

    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()

            # Check if the authenticated user is an admin
            if user.is_staff:
                auth.login(request, user)
                # messages.success(request, 'Admin login successful.')
                return redirect('admin_home')  # Update with the admin dashboard URL or view name
            else:
                messages.error(request, 'Invalid credentials. You are not an admin.')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    else:
        form = AuthenticationForm()

    return render(request, 'admin_signin.html', {'form': form})


@login_required(login_url='admin/')
def admin_home(request):
    user_profile = Profile.objects.all()

    context = {
        'user_profile': user_profile
    }
    return render(request, 'admin_home.html', context)


@login_required(login_url='admin/')
def admin_logout(request):
    logout(request)
    return redirect('admin_home')


@login_required(login_url='admin/')
def admin_search(request):
    try:

        user_profile = Profile.objects.get(user=request.user)

    except Profile.DoesNotExist:

        user_profile = None

    username_profile_list = []

    if request.method == 'POST':
        username = request.POST.get('username', '')

        # Use __icontains to perform case-insensitive search on username
        username_objects = User.objects.filter(username__icontains=username)

        # Use __in lookup to fetch profiles in a single query
        profile_lists = Profile.objects.filter(user__in=username_objects)

        # Avoiding N+1 query issue by prefetching related user data
        username_profile_list = profile_lists.select_related('user')

    return render(request, 'admin_search_user_list.html',
                  {'user_profile': user_profile, 'username_profile_list': username_profile_list})


# def admin_delete_user(request):
# user_to_delete = get_object_or_404(User, username=username)
# print(user_to_delete)
#
#
# user_to_delete.delete()
# return redirect('admin_home')

@login_required(login_url='admin/')
def admin_delete_user(request, username):
    # Get the current user and profile
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)

    # Store the previous username in DeletedUserRecord
    DeletedUserRecord.objects.create(previous_username=user.username)

    # Anonymize the user by changing the username
    user.username = False
    user.save()

    # Delete related data (adjust this based on your actual model relationships)
    # For example, if you have related models, you need to delete them explicitly
    profile.delete()

    # Redirect to the home page or any other desired page
    # return redirect('admin_home')  # Replace 'home' with the URL or view name you want to redirect to
    return render(request, 'admin_search_user_list.html', {'username': username})


@login_required(login_url='admin/')
def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect('admin_user_detail', pk=post.user)


@login_required(login_url='admin/')
def admin_user_detail(request, pk):
    user_object = get_object_or_404(User, username=pk)
    user_profile = get_object_or_404(Profile, user=user_object)
    user_post = Post.objects.filter(user=pk)
    user_post_length = len(user_post)

    follower = request.user.username
    user = pk

    # if FollowersCount.objects.filter(follower=follower, user=user).first():
    #     button_text = 'Unfollow'
    # else:
    #     button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_post_length': user_post_length,
        'user_post': user_post,
        # 'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
        'account_settings_url': reverse('admin_user_create'),

    }
    return render(request, 'admin_user_detail.html', context)


@login_required(login_url='admin/')
def admin_user_create(request, username):
    # Fetch the user based on the provided username
    user = get_object_or_404(User, username=username)

    # Attempt to get the existing profile or create a new one
    user_profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        if request.FILES.get('image') is None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        if request.FILES.get('image') is not None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect('admin_user_create', username=username)

    return render(request, 'admin_user_create.html', {'user_profile': user_profile})
