
#include <gazebo/gazebo.hh>
#include <ignition/math.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <stdio.h>

namespace gazebo
{
  class R2L_94_2 : public ModelPlugin
  {
    public: void Load(physics::ModelPtr _parent, sdf::ElementPtr /*_sdf*/)
    {
      // Store the pointer to the model
      this->model = _parent;

        // create the animation
        gazebo::common::PoseAnimationPtr anim(
              // name the animation 'R2L_94_2',
              // make it last 10 seconds,
              // and set it on a repeat loop
              new gazebo::common::PoseAnimation("R2L_94_2", 5.26, true));

        gazebo::common::PoseKeyFrame *key;

        key = anim->CreateKeyFrame(0.00);
        key->Translation(ignition::math::Vector3d(-4.50, 5.06, 0));
        key->Rotation(ignition::math::Quaterniond(0, 0, 0));

        key = anim->CreateKeyFrame(5.26);
        key->Translation(ignition::math::Vector3d(0.00, 7.19, 0));
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
  GZ_REGISTER_MODEL_PLUGIN(R2L_94_2)
}