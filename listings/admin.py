from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import AdminSite
from django.templatetags.static import static
from .models import Rental, RegisterDb, RentalImage
from django.utils.html import mark_safe

# Customizing admin site header and title
admin.site.site_header = _('Apcostays Admin Panel')
admin.site.site_title = _('Apcostays Admin')
admin.site.index_title = _('Welcome to Apcostays Admin Panel')

# Custom Admin Site for changing headers and titles
class CustomAdminSite(AdminSite):
    site_header = "Apcostays Admin Panel"
    site_title = "Apcostays Admin"
    index_title = "Apcostays Admin"

    # Add custom CSS to the admin interface
    class Media:
        css = {
            'all': [static('css/admin_custom.css')],  # Ensure the correct path is set
        }

# Inline model for RentalImage with image preview
class RentalImageInline(admin.TabularInline):
    model = RentalImage
    extra = 1  # Show an extra empty form for adding new images
    readonly_fields = ['preview_image']
    fields = ('preview_image', 'image')  # Ensuring the fields appear in the right order

    def preview_image(self, obj):
        """Show an image preview inside the inline admin panel."""
        return mark_safe(f'<img src="{obj.image.url}" width="100" style="border-radius: 5px;" />') if obj.image else "No Image"

    preview_image.short_description = "Image Preview"

# Customize the Rental model in the admin panel
class RentalAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'rent', 'location', 'owner', 'owner_phone', 'verified')
    list_filter = ('verified', 'property_type', 'location')
    search_fields = ('title', 'location', 'owner__Name')
    list_editable = ('verified',)
    actions = ['approve_rentals', 'reject_rentals']
    inlines = [RentalImageInline]  # Inline images
    list_per_page = 20  # Pagination for the Rental list

    def owner_phone(self, obj):
        return obj.owner.Phone  # Fetch owner's phone from RegisterDb model
    
    owner_phone.short_description = "Owner Phone"  # Column name in the admin panel

    def approve_rentals(self, request, queryset):
        """Approve selected rentals"""
        queryset.update(verified=True)

    def reject_rentals(self, request, queryset):
        """Reject selected rentals"""
        queryset.update(verified=False)

    approve_rentals.short_description = "Mark selected rentals as approved"
    reject_rentals.short_description = "Mark selected rentals as rejected"

# Customize the RegisterDb model in the admin panel
class RegisterDbAdmin(admin.ModelAdmin):
    list_display = ('Name', 'Email', 'Location', 'Phone')
    search_fields = ('Name', 'Email', 'Phone')
    list_per_page = 20  # Pagination for the RegisterDb list

# RentalImageAdmin to display images in the admin
class RentalImageAdmin(admin.ModelAdmin):
    list_display = ('rental', 'preview_image')
    list_per_page = 20  # Pagination for the RentalImage list

    def preview_image(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="100" style="border-radius: 5px;" />') if obj.image else "No Image"

# Register models with the default admin site (default admin)
admin.site.register(Rental, RentalAdmin)
admin.site.register(RentalImage, RentalImageAdmin)
admin.site.register(RegisterDb, RegisterDbAdmin)

# Register models with the custom admin site (custom admin)
admin_site = CustomAdminSite(name='custom_admin')
admin_site.register(Rental, RentalAdmin)
admin_site.register(RentalImage, RentalImageAdmin)
admin_site.register(RegisterDb, RegisterDbAdmin)
