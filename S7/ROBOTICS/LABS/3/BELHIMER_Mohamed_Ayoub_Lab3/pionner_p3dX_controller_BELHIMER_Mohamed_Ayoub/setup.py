import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'pionner_p3dX_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ayub',
    maintainer_email='belhimer.ayoub1608@gmail.com',
    description='Pose controller for Pioneer P3-DX robot',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'pose_controller = pionner_p3dX_controller.pionner_p3dX_pose_controller:main',
            'enhanced_pose_controller = pionner_p3dX_controller.enhanced_pose_controller:main',
        ],
    },
)
