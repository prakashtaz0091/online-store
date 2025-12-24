from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .serializers import ReviewSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Review


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_or_update_review(request):
    serializer = ReviewSerializer(
        data=request.data,
        context={"request": request},
    )

    serializer.is_valid(raise_exception=True)

    product = serializer.validated_data["product"]
    user = request.user

    review = Review.objects.filter(user=user, product=product).first()

    if review:
        # UPDATE
        serializer = ReviewSerializer(
            review,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # CREATE
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)
