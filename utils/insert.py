from . import models

# defaults = {'first_name': 'Bob'}
# try:
#     obj = Person.objects.get(first_name='John', last_name='Lennon')
#     for key, value in defaults.items():
#         setattr(obj, key, value)
#     obj.save()
# except Person.DoesNotExist:
#     new_values = {'first_name': 'John', 'last_name': 'Lennon'}
#     new_values.update(defaults)
#     obj = Person(**new_values)
#     obj.save()


class RecordNewReservation:
    def __init__(self, **kwargs):
        pass


class AddingNewReservationToDb:
    def __init__(self, request, **kwargs):
        number_kg = int(request.POST['number_of_kg_reserved'])
        price = int(request.POST['price'])

        reservation = models.Reservations(
            post=int(request.POST['post_id']),
            poster=int(request.POST['poster_id']),
            reserver=request.session['user_id'],
            nbr_kilos=int(request.POST['number_of_kg_reserved']),
            total_price=number_kg*price,
            post_code=request.POST['post_code'],
            post_state=request.POST['post_state'],
        )
        reservation.save()


class ToSignUpModel:
    def __init__(self, data_from_form):
        form = data_from_form
        model = models.SignUpModel(
            gender=form.cleaned_data['gender'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            address_email=form.cleaned_data['address_email'],
            phone_number=form.cleaned_data['phone_number'],
            language=form.cleaned_data['language'],
            password='tako',
            country=form.cleaned_data['country'],
            account_type=form.cleaned_data['account_type'],
        )
        model.save()

        # form_is_valid = True
        # print('=======', data_from_form.cleaned_data['first_name'])
        # subject = 'Inscription sur envoyer vos colis'
        # body = {
        #     'first_name': data_from_form.cleaned_data['first_name'],
        #     'last_name': data_from_form.cleaned_data['last_name'],
        #     'email': data_from_form.cleaned_data['address_email'],
        #     'message': 'Bonjour les amis',
        # }
        # message = "\n".join(body.values())
        # send_to = 'moutraoree@gmail.com'
        # try:
        #     send_mail(subject, message, send_to, [send_to])
        # except BadHeaderError:
        #     return HttpResponse('Invalid header found')
        # return redirect("main: homepage")

