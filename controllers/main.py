from odoo import http, _
from odoo.http import request
import json


class HostelBookingController(http.Controller):

    @http.route('/hostel/booking', type='http', auth='public', website=True, sitemap=True)
    def booking_page(self, **kwargs):
        """Display the hostel booking page."""
        hostels = request.env['hostel.hostel'].sudo().search([])
        return request.render('hostel_allocation.website_hostel_booking', {
            'hostels': hostels,
        })

    @http.route('/hostel/booking/submit', type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def submit_booking(self, **post):
        """Handle booking form submission."""
        error = {}

        name = post.get('name', '').strip()
        email = post.get('email', '').strip()
        phone = post.get('phone', '').strip()
        hostel_id = post.get('hostel_id')
        room_id = post.get('room_id')
        mess_id = post.get('mess_id')
        check_in_date = post.get('check_in_date')
        check_out_date = post.get('check_out_date')

        # Validation
        if not name:
            error['name'] = _('Name is required.')
        if not email:
            error['email'] = _('Email is required.')
        if not hostel_id:
            error['hostel_id'] = _('Please select a hostel.')
        if not room_id:
            error['room_id'] = _('Please select a room.')
        if not check_in_date:
            error['check_in_date'] = _('Check-in date is required.')
        if not check_out_date:
            error['check_out_date'] = _('Check-out date is required.')
        if check_in_date and check_out_date and check_out_date <= check_in_date:
            error['check_out_date'] = _('Check-out date must be after check-in date.')

        if error:
            hostels = request.env['hostel.hostel'].sudo().search([])
            return request.render('hostel_allocation.website_hostel_booking', {
                'hostels': hostels,
                'error': error,
                'form_data': post,
            })

        # Verify room exists and belongs to hostel
        room = request.env['hostel.room'].sudo().browse(int(room_id))
        if not room.exists() or room.hostel_id.id != int(hostel_id):
            hostels = request.env['hostel.hostel'].sudo().search([])
            return request.render('hostel_allocation.website_hostel_booking', {
                'hostels': hostels,
                'error': {'room_id': _('Invalid room selection.')},
                'form_data': post,
            })

        # Find first available bed in the room
        available_bed = request.env['hostel.bed'].sudo().search([
            ('room_id', '=', int(room_id)),
            ('status', '=', 'available'),
        ], limit=1)

        if not available_bed:
            hostels = request.env['hostel.hostel'].sudo().search([])
            return request.render('hostel_allocation.website_hostel_booking', {
                'hostels': hostels,
                'error': {'room_id': _('No available beds in this room. Please select another.')},
                'form_data': post,
            })

        # Create tenant record
        vals = {
            'name': name,
            'email': email,
            'phone': phone,
            'hostel_id': int(hostel_id),
            'room_id': int(room_id),
            'bed_id': available_bed.id,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'booking_source': 'website',
            'booking_status': 'submitted',
            'status': 'active',
        }
        if mess_id:
            vals['mess_id'] = int(mess_id)

        tenant = request.env['hostel.tenant'].sudo().create(vals)

        # Send confirmation email
        template = request.env.ref(
            'hostel_allocation.mail_template_booking_confirmation',
            raise_if_not_found=False,
        )
        if template and tenant.email:
            template.sudo().send_mail(tenant.id, force_send=True)

        return request.render('hostel_allocation.website_booking_success', {
            'tenant': tenant,
        })

    @http.route('/hostel/booking/get_rooms', type='json', auth='public', website=True)
    def get_rooms(self, hostel_id=None, **kwargs):
        """Return available rooms for a hostel."""
        if not hostel_id:
            return []
        
        rooms = request.env['hostel.room'].sudo().search([
            ('hostel_id', '=', int(hostel_id)),
            ('status', '=', 'available'),
        ])
        
        result = []
        for room in rooms:
            if room.available_bed_count > 0:
                result.append({
                    'id': room.id,
                    'name': room.name,
                    'floor': room.floor,
                    'available_beds': room.available_bed_count,
                })
        
        return result

    @http.route('/hostel/booking/get_mess_plans', type='json', auth='public', website=True)
    def get_mess_plans(self, hostel_id=None, **kwargs):
        """Return mess plans for a hostel."""
        if not hostel_id:
            return []
        
        plans = request.env['hostel.mess'].sudo().search([
            ('hostel_id', '=', int(hostel_id)),
            ('active', '=', True),
        ])
        
        result = []
        for plan in plans:
            result.append({
                'id': plan.id,
                'name': plan.name,
                'meal_type': plan.meal_type,
                'plan_type': plan.plan_type,
                'price': plan.price,
            })
        
        return result
