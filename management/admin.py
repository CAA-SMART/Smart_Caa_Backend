
from django.contrib import admin
from .models.account_type import AccountType
from .models.payment_period import PaymentPeriod
from .models.payment_plan import PaymentPlan
from .models.account import Account
from .models.account_user import AccountUser

@admin.register(AccountUser)
class AccountUserAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "name", "cpf", "created_at")
    search_fields = ("name", "cpf")
    list_filter = ("account",)

class AccountUserInline(admin.TabularInline):
	model = AccountUser
	extra = 1
	fields = ("name", "cpf", "is_active")
	show_change_link = True

@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "description", "is_active", "created_at")
	search_fields = ("name", "description")
	list_filter = ("is_active",)


@admin.register(PaymentPeriod)
class PaymentPeriodAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "description", "is_active", "created_at")
	search_fields = ("name", "description")
	list_filter = ("is_active",)


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"name",
		"description",
		"user_limit",
		"custom_pictograms_per_patient",
		"attachments_per_patient",
		"is_active",
		"created_at"
	)
	search_fields = ("name", "description")
	list_filter = ("is_active",)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"name",
		"account_type",
		"payment_period",
		"payment_plan",
		"due_day",
		"start_date",
		"first_due_date",
		"end_date",
		"responsible_name",
		"responsible_phone",
		"responsible_email",
		"auto_renewal",
		"is_active",
		"created_at"
	)
	search_fields = ("name", "responsible_name", "responsible_email")
	list_filter = ("account_type", "payment_period", "payment_plan", "is_active", "auto_renewal")
	inlines = [AccountUserInline]
