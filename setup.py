try:
    from setuptools import setup, find_packages
except ImportError:
    import sys
    print("setuptools is not installed. Please install it using: pip install setuptools")
    sys.exit(1)

from typing import List

def get_requirements()-> List[str]:
    '''
    Description: This function is going to return list of requirements mentioned in requirements.txt file
    '''
    requirement_lst:List[str] = []
    try:
        with open('requirements.txt','r', encoding='utf-8') as file:
            lines = file.readlines()
        # read lines from the file
        for line in lines:
            requirement = line.strip()
            # ignore empty lines and -e. 
            if requirement and requirement != '-e .':  
                requirement_lst.append(requirement)
    except Exception as e:
        print(f"Error reading requirements.txt: {e}")
    
    return requirement_lst

setup(
    name='NetworkSecurity',
    version='0.0.1',
    author = 'Harish Kumar',
    author_email= "utaharish96@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_requirements(),
)