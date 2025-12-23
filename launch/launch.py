import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    ExecuteProcess,
    TimerAction
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # ---------------------------------------------------------
    # 1. PACKAGE PATHS
    # ---------------------------------------------------------
    pkg_ceto = get_package_share_directory('ceto_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    world_path = os.path.join(pkg_ceto, 'worlds', 'sauvc25.world')
    model_sdf = os.path.join(pkg_ceto, 'models', 'bluerov2', 'model.sdf')
    urdf_xacro = os.path.join(pkg_ceto, 'urdf', 'robot.urdf.xacro')
    rviz_config = os.path.join(pkg_ceto, 'rviz', 'default.rviz')
    bridge_config = os.path.join(pkg_ceto, 'config', 'bridge.yaml')

    model_dir = os.path.join(pkg_ceto, 'models')

    use_sim_time = LaunchConfiguration('use_sim_time')
    model_arg = LaunchConfiguration('model')
    rviz_arg = LaunchConfiguration('rvizconfig')

    # ---------------------------------------------------------
    # 2. ENVIRONMENT (make sure gz/gazebo can find models)
    # ---------------------------------------------------------
    # Append our package models to the various resource/model env vars used by gz/gazebo
    # Note: reads the current value of env in the launching process and appends to it.
    gazebo_model_path_action = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=model_dir + ':' + os.environ.get('GAZEBO_MODEL_PATH', '')
    )

    gz_sim_resource_path_action = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=model_dir + ':' + os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    )

    gz_resource_path_action = SetEnvironmentVariable(
        name='GZ_RESOURCE_PATH',
        value=model_dir + ':' + os.environ.get('GZ_RESOURCE_PATH', '')
    )

    # ---------------------------------------------------------
    # 3. START GZ-SIM (server + GUI)
    # ---------------------------------------------------------
    start_gazebo_cmd = ExecuteProcess(
        cmd=['gz', 'sim', '-r', '-v', '4', world_path],
        output='screen',
        additional_env={
            'GAZEBO_MODEL_PATH': model_dir + ':' + os.environ.get('GAZEBO_MODEL_PATH', ''),
            'GZ_SIM_RESOURCE_PATH': model_dir + ':' + os.environ.get('GZ_SIM_RESOURCE_PATH', ''),
            'GZ_RESOURCE_PATH': model_dir + ':' + os.environ.get('GZ_RESOURCE_PATH', '')
        }
    )

    # ---------------------------------------------------------
    # 4. ROBOT DESCRIPTION (URDF → TF)
    # ---------------------------------------------------------
    robot_description = ParameterValue(
        Command(['xacro ', model_arg]),
        value_type=str
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': use_sim_time},
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # 5. SPAWN THE BLUEROV2 MODEL (delayed to avoid race)
    # ---------------------------------------------------------
    spawn_bluerov2 = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-file', model_sdf,
            '-name', 'bluerov2',
            '-x', '0', '-y', '0', '-z', '0.0',
            '-R', '0', '-P', '0', '-Y', '0'
        ],
        output='screen'
    )

    # Delay the spawn a bit so gz-sim has time to start and register services
    spawn_bluerov2_delayed = TimerAction(
        period=3.0,
        actions=[spawn_bluerov2]
    )

    # ---------------------------------------------------------
    # 6. ROS-GZ BRIDGE
    # ---------------------------------------------------------
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': bridge_config,
            'qos_overrides./tf_static.publisher.reliability': 'reliable'
        }],
        output='screen'
    )

    # ---------------------------------------------------------
    # 7. RVIZ
    # ---------------------------------------------------------
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_arg],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # ---------------------------------------------------------
    # 8. LAUNCH DESCRIPTION
    # ---------------------------------------------------------
    return LaunchDescription([
        # Arguments
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'
        ),
        DeclareLaunchArgument(
            'model',
            default_value=urdf_xacro,
            description='Path to URDF/Xacro file'
        ),
        DeclareLaunchArgument(
            'rvizconfig',
            default_value=rviz_config,
            description='Path to RViz configuration'
        ),

        # Environment Variables (actions)
        gazebo_model_path_action,
        gz_sim_resource_path_action,
        gz_resource_path_action,

        # Start gz-sim (server + GUI)
        start_gazebo_cmd,

        # Nodes: spawn is delayed to avoid race with gz-sim start
        spawn_bluerov2_delayed,
        bridge,
        robot_state_publisher,
        rviz,
    ])
