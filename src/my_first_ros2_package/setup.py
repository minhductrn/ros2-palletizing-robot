import os
from glob import glob

from setuptools import find_packages, setup


package_name = 'my_first_ros2_package'


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),

    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')
        ),
        (
            os.path.join('share', package_name, 'config'),
            [
                'config/params.yaml',
                'config/controllers.yaml',
                'config/arm_controller.yaml',
            ]
        ),
        (
            os.path.join('share', package_name, 'urdf'),
            [
                'urdf/palletizing_robot.urdf'
            ]
        ),
    ],

    package_data={
        '': ['py.typed']
    },

    install_requires=[
        'setuptools'
    ],

    zip_safe=True,

    maintainer='MinhDuc Tran',
    maintainer_email='ductm.tran@gmail.com',
    description='ROS 2 palletizing robot learning project',
    license='TODO: License declaration',

    extras_require={
        'test': [
            'pytest',
        ],
    },

    entry_points={
        'console_scripts': [
            'hello_node = my_first_ros2_package.hello_node:main',
            'publisher_node = my_first_ros2_package.publisher_node:main',
            'subscriber_node = my_first_ros2_package.subscriber_node:main',
            'gripper_service_node = my_first_ros2_package.gripper_service_node:main',
            'palletize_action_server = my_first_ros2_package.palletize_action_server:main',
        ],
    },
)
