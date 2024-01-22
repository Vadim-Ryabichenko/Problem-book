from .models import TaskCard
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from .forms import TaskCardForm, SetExecutorForm
from django.urls import reverse
from django.contrib.auth.models import User



class MainView(TemplateView):
    template_name = "mainpage.html"


class AboutView(TemplateView):
    template_name = "about.html"


class TaskCardListView(ListView):
    model = TaskCard
    template_name = 'tasks.html'
    queryset = TaskCard.objects.all()
    context_object_name = 'task_list'


class TaskCardDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        task = get_object_or_404(TaskCard, pk=pk)
        context = {'task': task}
        return render(request, 'task_detail.html', context)
    

class TaskCardCreateView(LoginRequiredMixin, CreateView):
    template_name = 'task_create.html'
    http_method_names = ['get', 'post']
    form_class = TaskCardForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.creator = self.request.user
        obj.save()
        return super().form_valid(form=form)
    
    def get_success_url(self):
        return reverse('tasks')


class TaskCardUpdateView(LoginRequiredMixin, UpdateView):
    model = TaskCard
    template_name = 'task_update.html'
    form_class = TaskCardForm

    def get_initial(self):
        initial = super().get_initial()
        obj = self.get_object() 
        initial['text'] = obj.text
        return initial
    
    def get_success_url(self):
        pk = self.object.pk
        return reverse('task_detail', kwargs={'pk': pk})
    

class TaskCardDeleteView(LoginRequiredMixin, DeleteView):
    model = TaskCard

    def get_success_url(self):
        return reverse('tasks')
    
    
class UpperStatusTaskCardView(View):
    def post(self, request, pk):
        task = get_object_or_404(TaskCard, pk=pk)
        if task.status == 'New':
            task.status = 'In progress'
        elif task.status == 'In progress':
            task.status = 'In QA'
        elif task.status == 'In QA':
            task.status = 'Ready'
        elif task.status == 'Ready':
            task.status = 'Done'
        task.save()
        return redirect('tasks')
        

class LowerStatusTaskCardView(View):
    def post(self, request, pk):
        task = get_object_or_404(TaskCard, pk=pk)
        if task.status == 'In progress':
            task.status = 'New'
        elif task.status == 'In QA':
            task.status = 'In progress'
        elif task.status == 'Ready':
            task.status = 'In QA'
        elif task.status == 'Done':
            task.status = 'Ready'
        task.save()
        return redirect('tasks')
    

class SetExecutorView(View):
    template_name = 'tasks.html'

    def post(self, request, pk):
        task = get_object_or_404(TaskCard, pk=pk)
        form = SetExecutorForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
        return render(request, self.template_name, {'form': form, 'task': task})
