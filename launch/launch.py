import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
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
    # 2. ENVIRONMENT VARIABLES (RESOURCES FOR GAZEBO)
    # ---------------------------------------------------------
    existing_gz = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    existing_ign = os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')

    new_gz_path = f"{model_dir}:{existing_gz}" if existing_gz else model_dir
    new_ign_path = f"{model_dir}:{existing_ign}" if existing_ign else model_dir

    set_gz_env = SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', new_gz_path)
    set_ign_env = SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', new_ign_path)

    # ---------------------------------------------------------
    # 3. ROBOT DESCRIPTION (URDF → TF)
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
    # 4. GAZEBO SIM
    # ---------------------------------------------------------
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f"-r -v 4 {world_path}"
        }.items()
    )

    # ---------------------------------------------------------
    # 5. SPAWN THE BLUEROV2 MODEL
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

    # ---------------------------------------------------------
    # 6. ROS-GAZEBO BRIDGE
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
    # 7. STATIC TRANSFORM (gz model name → ros base_link)
    # ---------------------------------------------------------
    # tf_glue = Node(
    #     package='tf2_ros',
    #     executable='static_transform_publisher',
    #     arguments=['0', '0', '0', '0', '0', '0', 'bluerov2', 'base_link'],
    #     name='gz_to_ros_tf_publisher',
    #     output='screen'
    # )

    # ---------------------------------------------------------
    # 8. RVIZ
    # ---------------------------------------------------------
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_arg],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # ---------------------------------------------------------
    # 9. LAUNCH DESCRIPTION
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

        # Environment Variables
        set_gz_env,
        set_ign_env,

        # Nodes
        gazebo_sim,
        spawn_bluerov2,
        bridge,
        robot_state_publisher,
        # tf_glue,
        rviz,
    ])
