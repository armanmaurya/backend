from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication

from page.serializers import PageCreateFormSerializer
from .serializers import NotebookFormSerializer, NotebookGetSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Notebook
from page.models import Page
from page.views import getNotebookPage
from page.serializers import PageSerializer, PageUpdateFormSerializer

from users.models import CustomUser as User


class NoteBookPageView(APIView):
    authentication_classes = [SessionAuthentication]

    def get(self, request, username=None, slug=None, path=None):
        if slug and username and path:
            try:
                page = self.get_page(username, slug, path)
                serializer = PageSerializer(page)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Page.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND, data={"error": "Page not found"}
                )
            except Notebook.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND,
                    data={"error": "Notebook not found"},
                )
            except User.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND, data={"error": "User not found"}
                )
        elif slug and username:
            try:
                notebook = self.get_notebook(username, slug)
                serializer = NotebookGetSerializer(notebook)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Notebook.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND,
                    data={"error": "Notebook not found"},
                )
            except User.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND, data={"error": "User not found"}
                )
        elif username:
            try:
                user = User.objects.get(username=username)
                notebooks = Notebook.objects.filter(user=user)
                notebook_serializer = NotebookGetSerializer(notebooks, many=True)
                return Response(notebook_serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "User not found"})
        
        all_notebooks = Notebook.objects.all()
        serializer = NotebookGetSerializer(all_notebooks, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    # @permission_classes([IsAuthenticated])
    def post(self, request, username=None, slug=None, path=None):
        """
        {
            title: "Page title",
        }
        """
        # logged_user = request.user
        # if logged_user != request_user:
        #     return Response(status=status.HTTP_401_UNAUTHORIZED, data={"error": "Unauthorized"})
        try:
            # request_user = User.objects.get(username=username)
            serializer = PageCreateFormSerializer(data=request.data)
            notebook = self.get_notebook(username, slug)
            parent = None
            if path != None:
                parent = getNotebookPage(notebook, path)
            if serializer.is_valid():
                serializer.save(notebook=notebook, parent=parent)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Page.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND, data={"error": "Page not found"}
                )
        except Notebook.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"error": "Notebook not found"},
            )
        except User.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"error": "User not found"}
            )

    @permission_classes([IsAuthenticated])
    def patch(self, request, username=None, slug=None, path=None):
        """
        {
            "title": "New title", (optional)
            "content": "New content" (optional)
        }
        """
        if slug and username and path:
            try:
                page = self.get_page(username, slug, path)
                serializer = PageUpdateFormSerializer(page, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Page.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND, data={"error": "Page not found"}
                )
            except Notebook.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND,
                    data={"error": "Notebook not found"},
                )
            except User.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND, data={"error": "User not found"}
                )
        elif slug and username:
            try:
                notebook = self.get_notebook(username, slug)
                serializer = NotebookGetSerializer(notebook)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Notebook.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND,
                    data={"error": "Notebook not found"},
                )
            except User.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND, data={"error": "User not found"}
                )
        return Response(status=status.HTTP_404_NOT_FOUND)


    # @permission_classes([IsAuthenticated])
    def delete(self, request, username=None, slug=None, path=None):
        if username and slug and path:
            try:
                page = self.get_page(username, slug, path)
                page.delete()
            except Page.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND, data={"error": "Page not found"}
                )
            except Notebook.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND,
                    data={"error": "Notebook not found"},
                )
            except User.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND, data={"error": "User not found"}
                )
            return Response(
                status=status.HTTP_204_NO_CONTENT,
                data={"message": "Page deleted successfully"},
            )

        elif username and slug:
            try:
                notebook = self.get_notebook(username, slug)
                notebook.delete
                return Response(
                    status=status.HTTP_204_NO_CONTENT,
                    data={"message": "Notebook deleted successfully"},
                )
            except Notebook.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND,
                    data={"error": "Notebook not found"},
                )
            except User.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND, data={"error": "User not found"}
                )
        return Response(status=status.HTTP_404_NOT_FOUND)

    def get_page(self, username, slug, path):
        notebook = self.get_notebook(username, slug)
        page = getNotebookPage(notebook, path)
        return page

    def get_notebook(self, username, slug):
        user = User.objects.get(username=username)
        notebook = Notebook.objects.get(slug=slug, user=user)
        return notebook
