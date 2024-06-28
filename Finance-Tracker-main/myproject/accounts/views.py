from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm, LoginForm
# accounts/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'accounts/home.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Replace 'home' with your home view name
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('welcome')  # Replace 'home' with your home view name
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')  # Replace 'login' with your login view name
from django.contrib.auth.decorators import login_required

@login_required
def welcome(request):
    return render(request, 'accounts/welcome.html')

# accounts/views.py

from django.shortcuts import render, redirect
from .forms import AddItemForm, RemoveItemForm
from .models import FinancialItem
from django.contrib.auth.decorators import login_required
# accounts/views.py

from django.shortcuts import render, redirect
from .forms import AddItemForm, RemoveItemForm, SetBudgetForm
from .models import FinancialItem, UserProfile
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from collections import defaultdict
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FinancialItem, UserProfile
from .forms import AddItemForm, RemoveItemForm, SetBudgetForm

@login_required
def welcome(request):
    user = request.user
    items = FinancialItem.objects.filter(user=user)
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        if 'add_item' in request.POST:
            add_form = AddItemForm(request.POST)
            if add_form.is_valid():
                new_item = add_form.save(commit=False)
                new_item.user = user
                new_item.save()

                # Update progress bar and level number if item added for a new month
                latest_item = items.order_by('-year', '-month').first()
                # if latest_item and (latest_item.year != new_item.year or latest_item.month != new_item.month):
                #     user_profile.update_progress_and_level()
                if latest_item:
                    user_profile.update_progress_and_level(latest_item)
                
                return redirect('welcome')
        elif 'remove_item' in request.POST:
            remove_form = RemoveItemForm(request.POST)
            if remove_form.is_valid():
                item_id = remove_form.cleaned_data['item_id']
                FinancialItem.objects.filter(id=item_id, user=user).delete()
                return redirect('welcome')
        elif 'set_budget' in request.POST:
            budget_form = SetBudgetForm(request.POST, instance=user_profile)
            if budget_form.is_valid():
                budget_form.save()
                return redirect('welcome')
    else:
        add_form = AddItemForm()
        remove_form = RemoveItemForm()
        budget_form = SetBudgetForm(instance=user_profile)

    # Group items by tags
    items_by_tag = defaultdict(list)
    for item in items:
        items_by_tag[item.tag].append(item.name)

    # Check for budget exceedance
    expenses_per_month = defaultdict(lambda: 0)
    for item in items:
        key = (item.year, item.month)
        expenses_per_month[key] += item.cost

    exceeded_months = [f"{month}/{year}" for (year, month), total in expenses_per_month.items() if total > user_profile.monthly_budget]

    # Calculate current lives based on number of exceeded months
    if user_profile.monthly_budget > 0:
        current_lives = 3 - len(exceeded_months)
        current_lives = max(1, current_lives)  # Ensure lives don't go below 1
    else:
        current_lives = None  # No lives when budget is 0

    context = {
        'items': items,
        'add_form': add_form,
        'remove_form': remove_form,
        'budget_form': budget_form,
        'items_by_tag': dict(items_by_tag),
        'monthly_budget': user_profile.monthly_budget,
        'exceeded_months': exceeded_months,
        'current_lives': current_lives,
        'progress_bar': user_profile.progress_bar,
        'level_number': user_profile.level_number,
    }
    return render(request, 'accounts/welcome.html', context)

# accounts/views.py

from django.shortcuts import render
from .models import FinancialItem, UserProfile
import matplotlib.pyplot as plt
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required
def summary(request):
    items = FinancialItem.objects.filter(user=request.user)

    # Calculate total expenses per month
    expenses_per_month = {}
    for item in items:
        key = (item.year, item.month)
        if key in expenses_per_month:
            expenses_per_month[key] += item.cost
        else:
            expenses_per_month[key] = item.cost

    # Prepare data for plotting line graph
    sorted_months = sorted(expenses_per_month.keys())
    months = [f"{year}-{month}" for year, month in sorted_months]
    expenses = [expenses_per_month[key] for key in sorted_months]

    # Plotting expenses timeline (line graph)
    plt.figure(figsize=(10, 6))
    plt.plot(months, expenses, marker='o', linestyle='-', color='b')
    plt.title('Total Expenses Timeline')
    plt.xlabel('Month-Year')
    plt.ylabel('Total Expenses ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save line graph plot to a temporary file
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    line_plot_path = os.path.join(temp_dir, 'expense_timeline.png')
    plt.savefig(line_plot_path)
    plt.close()

    # Calculate total expenses per tag (for pie chart)
    tags_expenses = {}
    total_expenses = 0
    for item in items:
        if item.tag in tags_expenses:
            tags_expenses[item.tag] += item.cost
        else:
            tags_expenses[item.tag] = item.cost
        total_expenses += item.cost

    # Prepare data for plotting pie chart by tags
    tags = list(tags_expenses.keys())
    expenses_by_tag = list(tags_expenses.values())
    explode = [0.1] * len(tags)

    # Plotting expenses by tags (pie chart)
    plt.figure(figsize=(8, 8))
    plt.pie(expenses_by_tag, labels=tags, explode=explode, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    plt.title(f'Total Expenses: ${total_expenses}')

    # Save pie chart plot to a temporary file
    pie_plot_path = os.path.join(temp_dir, 'expense_summary_pie.png')
    plt.savefig(pie_plot_path)
    plt.close()

    context = {
        'line_plot_path': os.path.join(settings.MEDIA_URL, 'temp', 'expense_timeline.png'),
        'pie_plot_path': os.path.join(settings.MEDIA_URL, 'temp', 'expense_summary_pie.png'),
    }
    return render(request, 'accounts/summary.html', context)
# views.py
# views.py
# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import FinancialItem
import pandas as pd
import os
from django.conf import settings
from django.http import HttpResponseServerError
from prophet import Prophet
import matplotlib.pyplot as plt

@login_required
def predict(request):
    user = request.user
    items = FinancialItem.objects.filter(user=user)

    # Prepare data
    data = []
    for item in items:
        date = f"{item.year}-{item.month:02d}"
        data.append((date, float(item.cost)))  # Ensure cost is converted to float or int

    if not data:
        error_message = "No financial items found. Add financial data to make predictions."
        return HttpResponseServerError(error_message)

    try:
        # Create DataFrame from data
        df = pd.DataFrame(data, columns=['ds', 'y'])
        df['ds'] = pd.to_datetime(df['ds'])
        
        # Initialize Prophet model
        model = Prophet()
        model.fit(df)

        # Predict next month
        future = model.make_future_dataframe(periods=1, freq='M')
        forecast = model.predict(future)
        next_month_expense = forecast.iloc[-1]['yhat']
        next_month_expense = round(next_month_expense, 2)

        # Generate plot for Prophet forecast
        fig = model.plot(forecast)
        plot_path = os.path.join(settings.MEDIA_ROOT, 'temp', 'expense_prediction_prophet.png')
        plt.savefig(plot_path)
        plt.close(fig)

        context = {
            'next_month_expense': next_month_expense,
            'plot_path': os.path.join(settings.MEDIA_URL, 'temp', 'expense_prediction_prophet.png'),
        }
        return render(request, 'accounts/predict.html', context)

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        return HttpResponseServerError(error_message)



# accounts/views.py

from django.http import HttpResponse
import csv
from .models import FinancialItem

@login_required
def download_items_csv(request):
    user = request.user
    items = FinancialItem.objects.filter(user=user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="financial_items.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Cost', 'Tag'])

    for item in items:
        writer.writerow([item.name, item.cost, item.tag])

    return response
