from django.shortcuts import render,redirect
from app.models import Plan,Biodata
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required(login_url='login')
def plan(request):
    try:
        user_biodata = Biodata.objects.get(user=request.user)

        plan1 = Plan.objects.get(id=1)  # Retrieve all plans (free and premium)
        print(plan1)
        plan2 = Plan.objects.get(id=2)  # Retrieve all plans (free and premium)
        print(plan2)
        if request.method == 'POST':
            selected_plan_id = request.POST.get('plan_id')
            selected_plan = Plan.objects.get(id=selected_plan_id)
            biodata = Biodata.objects.get(user=request.user)  # Get biodata for the current user
            
            # Associate the selected plan with the biodata
            biodata.plan = selected_plan
            biodata.save()

            messages.success(request, f"You have selected the {selected_plan.name} plan!")
            return redirect('home')  # Redirect to home page or another page after selection

        return render(request, 'pages/plans.html', {'plan1': plan1, 'plan2': plan2})

    except Biodata.DoesNotExist:
        return redirect('biodata')

    