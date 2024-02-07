from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import TaskCard
from .forms import SetExecutorForm
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib import messages
from .middleware import AutoLogoutMiddleware




class TaskCardListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='myuser', password='mypass')
        self.task = TaskCard.objects.create(text='Task text', creator=self.user)

    def test_taskcard_list_context(self):
        self.client.force_login(self.user) 
        response = self.client.get(reverse('tasks'))  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks.html')
        self.assertContains(response, 'Task text')  
        form = response.context['form']
        self.assertIsInstance(form, SetExecutorForm)  
        self.assertEqual(form.user, self.user)  

    def test_set_executor_form(self):
        form_data = {'executor': self.user.id}
        form = SetExecutorForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())  
        if self.user.is_superuser:
            self.assertTrue(User.objects.filter(id=self.user.id).exists())  
        else:
            self.assertFalse(User.objects.exclude(id=self.user.id).exists()) 


class TaskCardDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='my2tuser', password='my2password')
        self.task = TaskCard.objects.create(text='Head task', creator=self.user)

    def test_task_card_detail_view(self):
        self.client.login(username='my2tuser', password='my2password')
        url = reverse('task_detail', kwargs={'pk': self.task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['task'], self.task)
        self.assertContains(response, 'Head task')
        self.assertContains(response, 'New')
        self.assertEqual(self.task.creator, self.user)


class TaskCardCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='olduser', password='oldtestpass')

    def test_create_newtask(self):
        self.client.login(username='olduser', password='oldtestpass')
        data = {'text': 'My old task text'}
        response = self.client.post(reverse('task_create'), data)
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(TaskCard.objects.count(), 1)
        new_task = TaskCard.objects.first()
        self.assertEqual(new_task.text, 'My old task text')
        self.assertEqual(new_task.creator, self.user)
        self.assertEqual(new_task.status, 'New')
        self.assertEqual(new_task.executor, None)
        self.assertEqual(new_task.create_at.minute, timezone.now().minute)


class TaskCardUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Misha', password='passpass')
        self.task = TaskCard.objects.create(text='Misha task', creator=self.user)
        self.url = reverse('task_update', kwargs={'pk': self.task.pk})
        self.client.login(username='Misha', password='passpass')

    def test_update_task(self):
        updated_text = 'Updated Misha task'
        self.assertEqual(self.task.status, 'New')
        response = self.client.post(self.url, {'text': updated_text})
        self.task.refresh_from_db()
        self.assertEqual(self.task.text, updated_text)
        task_detail_url = reverse('task_detail', kwargs={'pk': self.task.pk})
        self.assertRedirects(response, task_detail_url)
        self.assertEqual(self.task.status, 'New')


class TaskCardDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Homa', password='homapassword')
        self.task = TaskCard.objects.create(text='Homa task text', creator=self.user)
        self.delete_url = reverse('task_delete', kwargs={'pk': self.task.pk})

    def test_task_card_deleted_successfully(self):
        self.client.login(username='Homa', password='homapassword')
        self.assertEqual(TaskCard.objects.count(), 1)
        response = self.client.post(self.delete_url, follow=True)
        self.assertRedirects(response, reverse('tasks'))
        self.assertFalse(TaskCard.objects.filter(pk=self.task.pk).exists())
        self.assertEqual(TaskCard.objects.count(), 0)


class TaskCardModelTest(TestCase):
    def setUp(self):
        self.creator_user = User.objects.create_user(username='mycreator', password='mycreatorpassword')
    
    def test_task_defaults(self):
        task = TaskCard.objects.create(
            text='Default task',
            creator=self.creator_user
        )
        self.assertEqual(task.status, 'New')
        self.assertIsNone(task.executor)
        self.assertEqual(task.create_at.minute, timezone.now().minute)


class UpperStatusTaskCardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='simpleuser', password='simplepassword')
        self.task = TaskCard.objects.create(text = 'New simple task', status='New', creator=self.user)
        
    def test_upper_status_view(self):
        self.client.login(username='simpleuser', password='simplepassword')
        response = self.client.post(reverse('upper_task_status', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        updated_task = TaskCard.objects.get(pk=self.task.pk)
        self.assertEqual(updated_task.status, 'In progress')
        response = self.client.post(reverse('upper_task_status', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        updated_task = TaskCard.objects.get(pk=self.task.pk)
        self.assertEqual(updated_task.status, 'In QA')
        response = self.client.post(reverse('upper_task_status', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        updated_task = TaskCard.objects.get(pk=self.task.pk)
        self.assertEqual(updated_task.status, 'Ready')
        response = self.client.post(reverse('upper_task_status', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        updated_task = TaskCard.objects.get(pk=self.task.pk)
        self.assertEqual(updated_task.status, 'Done')
    

class LowerStatusTaskCardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='simpleuser2', password='simplepassword2')
        self.task = TaskCard.objects.create(text = 'New simple task2', status='Done', creator=self.user)
        
    def test_lower_status_view(self):
        self.client.login(username='simpleuser2', password='simplepassword2')
        response = self.client.post(reverse('lower_task_status', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        updated_task = TaskCard.objects.get(pk=self.task.pk)
        self.assertEqual(updated_task.status, 'Ready')
        response = self.client.post(reverse('lower_task_status', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        updated_task = TaskCard.objects.get(pk=self.task.pk)
        self.assertEqual(updated_task.status, 'In QA')
        response = self.client.post(reverse('lower_task_status', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        updated_task = TaskCard.objects.get(pk=self.task.pk)
        self.assertEqual(updated_task.status, 'In progress')
        response = self.client.post(reverse('lower_task_status', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        updated_task = TaskCard.objects.get(pk=self.task.pk)
        self.assertEqual(updated_task.status, 'New')


class SetExecutorViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='future_executor', password='executorpass')
        self.task = TaskCard.objects.create(text='Again task test', creator=self.user)
        self.new_user = User.objects.create_user(username='fall', password='fallpassword')

    def test_set_executor_view_post(self):
        self.client.login(username='future_executor', password='executorpass')
        data = {'executor': self.user.id}
        url = reverse('set_executor', kwargs={'pk': self.task.pk})
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  
        self.task.refresh_from_db()  
        self.assertEqual(self.task.executor, self.user)  

        
class TaskCardModelViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='Uuser', password='utestpassword')
        self.superuser = User.objects.create_superuser(username='admin', password='adminpassword')
        self.my_task = TaskCard.objects.create(text='Again task test', creator=self.user, executor = self.user)
        self.task_data = {'text': 'opopop test', 'creator': self.user.id}
        self.fall_user = User.objects.create_user(username='Fallman', password='fallmanpass')
        self.temp_task = TaskCard.objects.create(text='Tempa task test', status='Ready', creator=self.user)

    def test_create_task_card(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/tasks/', self.task_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], 'opopop test')
        
    def test_update_status_executor(self):
        self.client.force_authenticate(user=self.user)
        updated_data = {'status': 'In progress'}
        response = self.client.patch(f'/api/tasks/{self.my_task.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], updated_data['status'])

    def test_update_status_no_executor(self):
        self.client.force_authenticate(user=self.fall_user)
        updated_data = {'status': 'In progress'}
        response = self.client.patch(f'/api/tasks/{self.my_task.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_status_executor_over_one_step(self):
        self.client.force_authenticate(user=self.user)
        updated_data = {'status': 'In QA'}
        response = self.client.patch(f'/api/tasks/{self.my_task.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_status_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        updated_data = {'status': 'Done'}
        response = self.client.patch(f'/api/tasks/{self.temp_task.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], updated_data['status'])

    def test_set_executor_by_creator(self):
        self.client.force_authenticate(user=self.user)
        updated_data = {'executor': self.user.id}
        response = self.client.patch(f'/api/tasks/{self.temp_task.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['executor'], self.user.id)

    def test_set_executor_by_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        updated_data = {'executor': self.fall_user.id}
        response = self.client.patch(f'/api/tasks/{self.temp_task.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['executor'], self.fall_user.id)

    def test_set_executor_invalid(self):
        self.client.force_authenticate(user=self.user)
        updated_data = {'executor': self.superuser.id}
        response = self.client.patch(f'/api/tasks/{self.temp_task.id}/', updated_data)
        self.assertNotEqual(response.data['executor'], self.temp_task.id)

    def test_delete_task_by_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(f'/api/tasks/{self.my_task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        task_exists = TaskCard.objects.filter(id=self.my_task.id).exists()
        self.assertFalse(task_exists)

    def test_delete_task_invalid(self):
        self.client.force_authenticate(user=self.fall_user)
        self.client.delete(f'/api/tasks/{self.my_task.id}/')
        task_exists = TaskCard.objects.filter(id=self.my_task.id).exists()
        self.assertTrue(task_exists)

    def test_invalid_list(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TaskCardSearchTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='user1password')
        self.user2 = User.objects.create_user(username='user2', password='user2password')
        TaskCard.objects.create(text='text1', creator=self.user1, status='Ready', executor=self.user1)
        TaskCard.objects.create(text='text2', creator=self.user2, status='Done', executor=self.user2)
        TaskCard.objects.create(text='text3', creator=self.user2, status='In QA', executor=self.user2)
        TaskCard.objects.create(text='text4', creator=self.user2, status='Ready', executor=self.user2)

    def test_search(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/tasks/?search=Ready')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) 
        for task in response.data:
            self.assertNotIn('text', task)
            self.assertNotIn('status', task)
        response = self.client.get('/api/tasks/?search=New')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class AutoLogoutMiddlewareTestCase(TestCase):
    def setUp(self):
        self.middleware = AutoLogoutMiddleware(get_response=None)
        self.client = Client()
        self.user_to_log = User.objects.create_user(username='userlpg', password='logpassword')
    
    def test_autologout(self):
        self.client.login(username='userlpg', password='logpassword')
        last_activity = timezone.now() - timezone.timedelta(seconds=61)
        session = self.client.session
        session['last_activity'] = last_activity.isoformat()
        session.save()
        response = self.client.get('/')
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(messages_list[0].message, 'You have been inactive for more than 1 minute. You have been automatically logged out')