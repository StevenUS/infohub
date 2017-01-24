from __future__ import unicode_literals
from django.db import models
import re
import bcrypt
import datetime

class UserManager(models.Manager):
    def register(self, data):
        response = {}
        validationErrors = self.validateAllFields(data)

        if len(validationErrors) > 0:
            response["validated"] = False
            response["errors"] = validationErrors
            response["registered"] = False
        else:
            response["validated"] = True

            # Validation passed. Save the new user to the database,
            # but first check if the user already exists.
            if not len(User.objects.filter(name = data["Name"])) > 0: #assuming objects.filter is part of ORM
                newUser = User.objects.create(
                    name = data['Name'],
                    password = bcrypt.hashpw(data['Password'].encode(), bcrypt.gensalt()),
                    city = data['City']
                )

                response["registered"] = True
                response["user"] = newUser
            else:
                response["registered"] = False
                response["errors"] = [ "User already exists. Login instead." ]
        return response

    def login(self, data):
        response = {}
        badLoginMsg = "Unknown user email or bad password."
        existingUser = None
        try:
            existingUser = User.objects.filter(name = data['Name']) #objects.filter part of ORM?
            if bcrypt.hashpw(data['Password'].encode(), existingUser[0].password.encode()) != existingUser[0].password:
                response["logged_in"] = False
                response["errors"] = [ badLoginMsg ]
                return response
        except Exception, e:
              # Handle situation when the salt is bad, etc.
              response["logged_in"] = False
              response["errors"] = [ badLoginMsg ]
              print "Unexpected error: " + e.message
              return response

        # Login succeeded.
        response["logged_in"] = True
        response["user"] = existingUser[0]
        return response

    ####### Validation Helper Methods #######

    def validateAllFields(self, data):
        response = []

        self.validateNotBlank(data, response)
        self.validateName(data, response)
        self.validatePasswords(data, response)
        # self.validateCity(data, response)

        return response

    def validateNotBlank(self, data, errors):
        for key in data:
            if len(data[key]) < 1:
                errors.append(key + " is required.")

    def validateName(self, data, errors):
        MIN_NAME_LEN = 2

        if not data["Name"].isalpha():
            errors.append("Only alphamumeric characters are allowed for the name.")

        if len(data["Name"]) < MIN_NAME_LEN:
            errors.append("First and Last Names must contain at least two characters.")

    def validatePasswords(self, data, errors):
        MIN_PASSWORD = 8
        if len(data["Password"]) < MIN_PASSWORD:
            errors.append("The password must be at least " + str(MIN_PASSWORD) + " characters. Yours is only " + str(len(data["Password"])) + ".")

        if len(data["Password"]) != len(data["Confirmed Password"]):
            errors.append("The password and confirmed password do not match.")

    # def validateCity(self, data, errors):
    #     if len(data["City"]) < 1:
    #         errors.append("City can't be blank")

    ####### Validation Helper Methods Ends #######


class User(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
