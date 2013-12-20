from tastypie.authorization import Authorization


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
        return bundle.obj.user == bundle.request.user

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
        return bundle.request.user.is_staff or (bundle.obj.user == bundle.request.user)

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        return bundle.request.user.is_staff or (bundle.obj.user == bundle.request.user)