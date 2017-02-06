'out of framework' postgres utils for django.

a module which addresses one of my reservations about frameworks 
like django: the maintenance of everything in a database , including
operational code and metadata. this module deals with the 'sawing off the 
branch you're sitting' on problem: the django application cannot recover
or handle exceptions while operating on its own database since that's 
where all the application logic is stored . This means that all data
definition operations are essentially possible byzantine failures ,
obviating rolling your own smokes as we do here.

note the subprocess module wrappers for the postgres utils.
