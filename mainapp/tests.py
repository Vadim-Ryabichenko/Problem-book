from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import TaskCard
from .forms import SetExecutorForm
from django.utils import timezone



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
