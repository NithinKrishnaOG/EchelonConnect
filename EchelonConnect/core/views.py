from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .form import *
from itertools import chain
import random, uuid
from django.db import models
from django.http import HttpResponseBadRequest
from django.contrib.auth.views import PasswordChangeView, PasswordResetConfirmView
from django.urls import reverse_lazy


@login_required(login_url='signin')
def index(request):
    try:
        user_objects = User.objects.get(username=request.user.username)
        user_profile = Profile.objects.get(user=user_objects)

        user_following_list = []
        feed = []

        user_following = FollowersCount.objects.filter(follower=request.user.username)

        for users in user_following:
            user_following_list.append(users.user)

        for usernames in user_following_list:
            feed_list = Post.objects.filter(user=usernames)
            feed.append(feed_list)

        feed_list = list(chain(*feed))

        # user suggestion starts
        all_user = User.objects.all()
        user_following_all = []
        for user in user_following:
            user_list = User.objects.get(username=user.user)
            user_following_all.append(user_list)

        new_suggestions_list = [x for x in list(all_user) if (x not in list(user_following_all))]

        current_user = User.objects.filter(username=request.user.username)
        final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
        random.shuffle(final_suggestions_list)

        username_profile = []
        username_profile_list = []
        for users in final_suggestions_list:
            username_profile.append(users.id)
        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        suggestions_username_profile_list = list(chain(*username_profile_list))

        messages = Message.objects.all()

        return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list,
                                              'suggestions_username_profile_list': suggestions_username_profile_list[
                                                                                   :4], 'messages': messages})
    except User.DoesNotExist:

        return redirect('signin')
    except Profile.DoesNotExist:

        return redirect('signin')


@login_required(login_url='signin')
def upload(request):
    if request.method == "POST":
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        tags_input = request.POST.get('tags', '')  # Assuming tags are input as a comma-separated string

        allowed_file_types = ['image', 'video']

        if not any(image.content_type.startswith(file_type) for file_type in allowed_file_types):
            return HttpResponseBadRequest("Invalid file type. Please upload an image")

        new_post = Post.objects.create(user=user, image=image, caption=caption)

        # Split tags input into individual tags
        tags_list = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        # Get or create PostTag objects for each tag
        tags_objects = [PostTag.objects.get_or_create(name=tag)[0] for tag in tags_list]
        # Add the tags to the new post
        new_post.tags.add(*tags_objects)

        new_post.save()
        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='signin')
def uploadtext(request):
    if request.method == "POST":
        user = request.user.username
        text = request.POST['upload_text']
        new_post = Post.objects.create(user=user, text=text)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    username_profile = []
    username_profile_list = []

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html',
                  {'user_profile': user_profile, 'username_profile_list': username_profile_list})


@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')


@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_post = Post.objects.filter(user=pk)
    user_post_length = len(user_post)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_post_length': user_post_length,
        'user_post': user_post,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,

    }
    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/' + user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/' + user)

    else:
        return redirect('/')


@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        return redirect('settings')

    return render(request, 'setting.html', {'user_profile': user_profile})


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if username and email is not None:
            if password == password2:
                if User.objects.filter(email=email).exists():
                    messages.info(request, 'Email Taken')
                    return redirect(signup)
                elif User.objects.filter(username=username).exists():
                    messages.info(request, 'Username Taken')
                    return redirect(signup)
                elif len(password) < 8:
                    messages.info(request, 'Password Must Contain 8 Characters')
                    return redirect(signup)
                elif password.isdigit():
                    messages.info(request, 'Password Cannot be Fully Digit')
                    return redirect(signup)
                else:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    # log user in and redirect to setting page
                    user_login = auth.authenticate(username=username, password=password)
                    auth.login(request, user_login)
                    # create a profile object for the new user
                    user_model = User.objects.get(username=user)
                    new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                    new_profile.save()
                    return redirect('signin')
            else:
                messages.info(request, 'Password Not Matching')
                return redirect(signup)
        else:
            messages.info(request, 'Fill EveryThing')
            return redirect(signup)
    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        previous_username = DeletedUserRecord.objects.values_list('previous_username')
        if username == str(previous_username):
            messages.info(request, 'Your Account has been Banned')
        else:
            user = auth.authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect('/')
            else:
                messages.info(request, 'Credentials Invalid')
                return redirect('signin')
    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def chat(request, receiver_username):
    sender = request.user
    receiver = User.objects.get(username=receiver_username)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            Message.objects.create(sender=sender, receiver=receiver, content=content)
            return redirect('chat', receiver_username=receiver_username)
    else:
        form = MessageForm()

    messages = Message.objects.filter(
        (models.Q(sender=sender, receiver=receiver) | models.Q(sender=receiver, receiver=sender)))

    return render(request, 'chatdum.html', {'form': form, 'messages': messages, 'receiver': receiver})


class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangingForm
    success_url = reverse_lazy('password_success')


@login_required(login_url='signin')
def password_success(request):
    return render(request, 'password_success.html', {})


@login_required(login_url='signin')
def report_post_view(request, post_id):
    r_user = get_object_or_404(Post, id=post_id)
    r_post = get_object_or_404(Post, image=post_id)
    r_text = get_object_or_404(Post, text=post_id)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        reported_by = request.user
        report = Report.objects.create(
            reported_user=r_user,
            reported_by=reported_by,
            reason=reason
        )
        messages.success(request, 'Post reported successfully.')
        return redirect('profile')
    return render(request, 'report.html', {'r_user': r_user, 'r_post': r_post, 'r_text': r_text})


@login_required(login_url='signin')
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        if post.image:
            caption = request.POST['caption']
            tags_input = request.POST['tags']

            # Update the post fields
            post.caption = caption


            # Split tags input into individual tags
            tags_list = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            # Update or create PostTag objects for each tag
            post.tags.clear()  # Clear existing tags
            for tag_name in tags_list:
                post_tag, _ = PostTag.objects.get_or_create(name=tag_name)
                post.tags.add(post_tag)
        else:
            text = request.POST['text']
            post.text = text
        post.save()
        return redirect('edit_post', post_id)  # Redirect to profile page after saving

    return render(request, 'edit_post.html', {'post': post})


@login_required(login_url='signin')
def deletepost(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    # Redirect the user to a relevant page after deleting the post
    return redirect('profile', pk=post.user)
