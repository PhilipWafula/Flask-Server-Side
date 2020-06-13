# Contributing

When contributing to this repository, please first discuss the change you wish to make via issue the
[Issues Tracker](https://github.com/PhilipWafula/Flask-Server-Side/issues). 

Please note we have a [code of conduct](CODE_OF_CONDUCT.md), please follow it in all your interactions with the project.

## Testing
Please write pytest unit tests (and integration tests where applicable).

## Submitting changes
Please send a pull request with a clear description of what you've done. Please follow our coding conventions (below)
and make sure all of your commits are atomic (one feature per commit).

Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes
should look like this:

```shell script
$ git commit -m "A brief summary of the commit
>
> A paragraph describing what changed and its impact."
```

## Coding conventions
Start reading our code and you'll get the hang of it. We optimize for readability:
``
- We indent using **TABS**

- This is open source software. Consider the people who will read your code, and make it look nice for them. It's sort
of like driving a car: Perhaps you love doing donuts when you're alone, but with passengers the goal is to make the ride
as smooth as possible.

- Overflowing function parameters beyond the preconfigured line length are converted into single-column list for instance:
```python
def sample_functions(parameter,
                     parameter_1,
                     parameter_2,
                     parameter_3):
    pass
```

- Standard strings are represented using single-quotes 