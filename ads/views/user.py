import json

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from ads.models import User


class UserListView(ListView):
    model = User
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        # self.object_list = self.object_list.annotate(total_ads=Count("ad")).order_by("username")
        self.object_list = self.object_list.prefetch_related("locations").annotate(
            total_ads=Count('ad__is_published', filter=Q(ad__is_published=True))).order_by('username')
        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return JsonResponse({
            "items": [
                {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "role": user.role,
                    "age": user.age,
                    "locations": list(map(str, user.locations.all())),
                    "total_ads": user.total_ads,
            }
                for user in page_obj
            ],
            "num_pages": page_obj.paginator.num_pages,
            "total": page_obj.paginator.count,
        }
        )


class UserDetailView(DetailView):
    model = User

    def get(self, request, *args, **kwargs):
        user = self.get_object()

        return JsonResponse(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "role": user.role,
                "age": user.age,
                "locations": list(map(str, user.locations.all())),
                "total_ads": user.total_ads,
            }
        )


@method_decorator(csrf_exempt, name='dispatch')
class UserCreateView(CreateView):
    model = User
    fields = ("first_name", "last_name", "username", "role", "age", "locations",)

    def post(self, request, *args, **kwargs):
        user_data = json.loads(request.body)

        user = User.objects.create(
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            username=user_data["username"],
            role=user_data["role"],
            age=user_data["age"],
            locations=user_data["locations"],
        )

        return JsonResponse(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "role": user.role,
                "age": user.age,
                "locations": user.locations,
                "total_ads": user.total_ads,
            }
        )


@method_decorator(csrf_exempt, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ("first_name", "last_name", "username", "role", "age", "locations",)

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        user_data = json.loads(request.body)
        self.object.first_name = user_data["first_name"],
        self.object.last_name = user_data["last_name"],
        self.object.username = user_data["username"],
        self.object.role = user_data["role"],
        self.object.age = user_data["age"],
        self.object.locations = user_data["locations"],

        self.object.save()

        return JsonResponse(
            {
                "id": self.object.id,
                "first_name": self.object.first_name,
                "last_name": self.object.last_name,
                "username": self.object.username,
                "role": self.object.role,
                "age": self.object.age,
                "locations": self.object.locations,
                "total_ads": self.object.total_ads,
            }
        )


@method_decorator(csrf_exempt, name='dispatch')
class UserDeleteView(DeleteView):
    model = User
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({}, status=204)
