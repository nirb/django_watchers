from django.shortcuts import render
from django.template.loader import get_template
from core.defs import *
from core.watchers_fin import WatchersFin
from core.watchers_info import WatchersInfo
from dashboard.models import Advisor
from django.contrib.auth.decorators import login_required


@login_required
def monthly_reports_view(request):
    context = {"view": monthly_report_html(request.user.id)}
    return render(request, "reports/montly_report.html", context)


def monthly_report_html(user_id):
    # Fetch data from the database
    watchersFin = WatchersFin()
    watchersInfo = WatchersInfo()
    info = watchersInfo.get(user_id)
    html_content = "<h1>Monthly Report</h1>"
    html_content += "<h2>Total Sum of All Watchers per Currency:</h2>"

    for currency, watchers in info["currency_groups"].items():
        html_content += f"<h3>{currency}</h3>"
        html_content += "<table class='table'><tr>" + \
            get_th("Watcher") + \
            get_th("Value") + \
            get_th("Commited") + \
            get_th("Unfunded") + \
            get_th("Advisor") + \
            "</tr>"
        for watcher in watchers:
            watcher_info = watchersFin.get_watcher_info(watcher.id)
            if watcher_info != None:
                html_content += "<tr>" + \
                    get_td(watcher.name) + \
                    get_td(watcher_info[VALUE]) + \
                    get_td(watcher_info[COMMITMENT_CURRENCY]) + \
                    get_td(watcher_info[UNFUNDED_CURRENCY]) + \
                    get_td(watcher.advisor.name) + \
                    "</tr>"
        html_content += "</table>"  # show advisors
    html_content += "<h2>Advisors:</h2>"
    advisors = Advisor.objects.all()
    html_content += "<ul>"
    html_content += "<table class='table'><tr>" + \
        get_th("Name") + \
        get_th("Phone") + \
        get_th("Email") + \
        "</tr>"
    for advisor in advisors:
        html_content += "<tr>" + \
            get_td(advisor.name) + \
            get_td(advisor.phone) + \
            get_td(advisor.mail) + \
            "</tr>"
    html_content += "</table>"

    return html_content

    currency_totals = {}

    html_content += "<ul>"
    for watcher in watchers:
        currency = watcher.currency
        if currency not in currency_totals:
            currency_totals[currency] = 0
        currency_totals[currency] += 200  # watcher.current_value

    # Create HTML content

    html_content += "<ul>"
    for currency, total in currency_totals.items():
        html_content += f"<li>{currency}: {total}</li>"
    html_content += "</ul>"

    return html_content

    html_content += "<h2>List of All Watchers:</h2><ul>"
    for watcher in watchers:
        html_content += f"<li>Name: {watcher.name}</li>"
        html_content += f"<li>Current Value: {watcher.current_value}</li>"
        html_content += f"<li>Total Invested: {watcher.total_invested}</li>"
        html_content += f"<li>Total Commitment: {watcher.total_commitment}</li>"
        html_content += f"<li>Unfunded: {watcher.unfunded}</li>"
        html_content += "<br>"
    html_content += "</ul>"
    return html_content


def get_td(text):
    return f"<td style='padding-right: 16px;'>{text}</td>"


def get_th(text):
    return f"<th>{text}</th>"
