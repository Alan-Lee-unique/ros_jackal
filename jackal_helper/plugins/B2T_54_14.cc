
#include <gazebo/gazebo.hh>
#include <ignition/math.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <stdio.h>

namespace gazebo
{
  class B2T_54_14 : public ModelPlugin
  {
    public: void Load(physics::ModelPtr _parent, sdf::ElementPtr /*_sdf*/)
    {
      // Store the pointer to the model
      this->model = _parent;

        // create the animation
        gazebo::common::PoseAnimationPtr anim(
              // name the animation 'B2T_54_14',
              // make it last 10 seconds,
              // and set it on a repeat loop
              new gazebo::common::PoseAnimation("B2T_54_14", 8.52, true));

        gazebo::common::PoseKeyFrame *key;

        key = anim->CreateKeyFrame(0.00);
        key->Translation(ignition::math::Vector3d(-3.45, 5.00, 0));
        key->Rotation(ignition::math::Quaterniond(0, 0, 0));

        key = anim->CreateKeyFrame(8.52);
        key->Translation(ignition::math::Vector3d(-2.33, 9.50, 0));
        key->Rotation(ignition::math::Quaterniond(0, 0, 0));

        // set the animation
        _parent->SetAnimation(anim);
    }

    // Pointer to the model
    private: physics::ModelPtr model;

    // Pointer to the update event connection
    private: event::ConnectionPtr updateConnection;
  };

  // Register this plugin with the simulator
  GZ_REGISTER_MODEL_PLUGIN(B2T_54_14)
}