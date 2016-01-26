.. module:: dojo
   :synopsis: Training classes for functions and algorithms.

dojo - Training classes for functions and algorithms
====================================================

.. class:: Dojo(algorithms : sequence, environ : object[, runs=100])

   A simple testing class for competing algorithms. :class:`Dojo` is the base
   class for concrete implementations to measure the performance of algorithms
   that shall perform the same task.
   
   .. attribute:: algorithms
   
      The list of algorithms to compare
      
   .. attribute:: environ
   
      An arbeitrary object that simulates the execution environment for the
      algorithms. A copy of it will be passed as first argument to each
      algorithm. 
      
      .. note::
      
         The copy will be created via :func:`copy.deepcopy` to ensure that
         (hopefully) no value of the original environment will be modified by
         an algorithm. 

   .. attribute:: runs
   
      The number of consecutive runs for each algorithm.

   .. method:: train(*args) -> None
   
      Executes the algorithms, comparing their performance.
      
      This has to be implemented by inheriting classes.

.. class:: TimingDojo(algorithms : sequence, environ : object[, runs=100])

   A :class:`Dojo` implementation measuring the execution time of its
   algorithms.
   
   .. method:: train(*args) -> object
   
      Executes the algorithms and compares their run-time performance
      :attr:`Dojo.runs` is used to create a reliable average mean for the
      execution time and hence should not be chosen too small.

      The method will return the best performing algorithm.

.. class:: FitnessDojo(algorithms : sequence, environ : object[, runs=100[, cmpfunc=min]])

   A :class:`Dojo` implementation measuring the fitness of its algorithms.
   The fitness is determined by the passed *cmpfunc*.
   
   .. attribute:: cmpfunc
   
      Comparision function for the fitness measurement. It has to return a
      single object of a passed iterable and must accept a named argument
      ``key``, since its execution looks like ::
      
         dojo.cmpfunc(result_dict, key=result_dict.get)
   
   .. method:: train(*args) -> object
   
      Executes the algorithms and compares their return value, which *must* be
      a float. :attr:`Dojo.runs` is used to create a reliable average mean for
      the return value and hence should not be chosen too small.
