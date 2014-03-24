from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized

class DateaBaseAuthorization(Authorization):
    '''
    Per object authorization:
        - read: all allowed
        - update/put: is_staff / object owner
        - delete: is_staff / object owner
    '''

    def read_list(self, object_list, bundle):
        # This assumes a ``QuerySet`` from ``ModelResource``.
        return object_list

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        return True

    def create_list(self, object_list, bundle):
        # Sorry user, no list creates
        raise Unauthorized("Sorry, no list create.")

    def create_detail(self, object_list, bundle):
        user = bundle.request.user
        if not user or not user.is_active or not user.email or user.status != 1:
            raise Unauthorized('user is not active or needs to validate email')
            return False
        return True

    def update_list(self, object_list, bundle):
        return False
        '''
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)

        return allowed
        '''

    def update_detail(self, object_list, bundle):
        user = bundle.request.user

        if not user or not user.is_active:
            raise Unauthorized('Not authenticated or inactive user')
            return False
        
        elif bundle.obj._meta.model_name == 'user':
            if user.is_staff or (bundle.obj == user and bundle.obj.status != 2):
                return True
            else:
                raise Unauthorized('Not authorized to change user')
                return False

        elif not user.email or user.status != 1:
            raise Unauthorized('User needs to validate email or has been banned')
            return False

        elif hasattr(bundle.obj, 'user'):
            if user.is_staff or (bundle.obj.user == user):
                return True
            else:
                raise Unauthorized('Can only change own user')
                return False
        return True

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        print "DELETE LIST"
        raise Unauthorized("Sorry, no list deletes.")

    def delete_detail(self, object_list, bundle):
        print "DELETE DETAIL"
        user = bundle.request.user
        print user
        if not user or not user.is_active or not user.email or user.status != 1:
            print "DETAIL UNAUTHORIZED"
            raise Unauthorized('user is not active or needs to validate email')

        print "RESULT: ", user.is_staff or (bundle.obj.user == user)
        return user.is_staff or (bundle.obj.user == user)



class OwnerOnlyAuthorization(Authorization):

    def read_list(self, object_list, bundle):

        if not bundle.request.user.is_authenticated():
            return []

        allowed = []
        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if hasattr(obj, 'user') and obj.user == bundle.request.user:
                allowed.append(obj)
            elif obj._meta.model_name == 'user' and obj == bundle.request.user:
                allowed.append(obj)

        return allowed
        

    def read_detail(self, object_list, bundle):

        if not bundle.request.user.is_authenticated():
            return False

        if request.user.is_active and request.user.status != 2 and bundle.obj.user == bundle.request.user:
            return True
        else:
            raise Unauthorized("Can only see one's own settings")

    def create_list(self, object_list, bundle):
        raise Unauthorized('No list create. Only detail allowed')

    def create_detail(self, object_list, bundle):
        user = bundle.request.user
        if not user or not user.is_active or not user.email or user.status != 1:
            raise Unauthorized('user is not active or needs to validate email')
            return False
        return True

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no list updates.")

    def update_detail(self, object_list, bundle):
        if request.user.is_active and request.user.status != 2 and bundle.obj.user == bundle.request.user:
            return True
        else:
            raise Unauthorized("Can only update one's own settings")

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no list deletes.")

    def delete_detail(self, object_list, bundle):
        user = bundle.request.user
        if not user or not user.is_active or not user.email or user.status != 1:
            raise Unauthorized('user is not active or needs to validate email')
        return user.is_staff or (bundle.obj.user == user)



