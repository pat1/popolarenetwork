from distutils.core import setup
from popolarenetwork import __version__

setup(name='popolarenetwork',
      version=__version__,
      description='recorder for popolare network radio broadcast',
      author='Paolo Patruno',
      author_email='p.patruno@iperbole.bologna.it',
      platforms = ["any"],
      url='https://github.com/pat1/popolarenetwork',
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Operating System :: OS Independent",
      ],
      packages=['popolarenetwork'],
      scripts=['popolarenetworkd'],
      data_files=(('/etc/popolarenetwork',['popolarenetwork-site.cfg',]),),
      license = "GNU GPL v2",
      requires= [ "mutagen","django","reportlab","configobj"],
      long_description="""\ 
      recorder for popolare network radio broadcast
      https://github.com/pat1/popolarenetwork
      """
      )
