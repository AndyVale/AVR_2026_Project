#include "SimModeWorldBase.h"
#include "physics/FastPhysicsEngine.hpp"
#include "physics/ExternalPhysicsEngine.hpp"
#include <exception>
#include "AirBlueprintLib.h"

void ASimModeWorldBase::BeginPlay()
{
    Super::BeginPlay();
}

void ASimModeWorldBase::initializeForPlay()
{
    std::vector<msr::airlib::UpdatableObject*> drone_vehicles;

    for (auto& api : getApiProvider()->getVehicleSimApis()) {
        if (api->getVehicleSetting()->vehicle_type != AirSimSettings::kVehicleTypePhysXCar) {
            // Drones go to the background physics thread
            drone_vehicles.push_back(api);
        }
        else {
            // MULTIDOMAIN FIX: Cars aren't in the physics world, 
            // so we must reset them manually here so they are 
            // ready for the very first Tick().
            api->reset();
        }
    }

    std::unique_ptr<PhysicsEngineBase> physics_engine = createPhysicsEngine();
    physics_engine_ = physics_engine.get();
    physics_world_.reset(new msr::airlib::PhysicsWorld(std::move(physics_engine),
                                                        drone_vehicles,
                                                        getPhysicsLoopPeriod()));
}

void ASimModeWorldBase::registerPhysicsBody(msr::airlib::VehicleSimApiBase* physicsBody)
{
    // Check if it is a car
    if (physicsBody->getVehicleSetting()->vehicle_type == AirSimSettings::kVehicleTypePhysXCar) {
        physicsBody->reset(); // Initialize for Game Thread
    }
    else {
        physicsBody->reset(); // Initialize for Physics Thread
        physics_world_.get()->addBody(physicsBody);
    }
}


void ASimModeWorldBase::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    //remove everything that we created in BeginPlay
    physics_world_.reset();

    Super::EndPlay(EndPlayReason);
}

void ASimModeWorldBase::startAsyncUpdator()
{
    physics_world_->startAsyncUpdator();
}

void ASimModeWorldBase::stopAsyncUpdator()
{
    physics_world_->stopAsyncUpdator();
}

long long ASimModeWorldBase::getPhysicsLoopPeriod() const //nanoseconds
{
    return physics_loop_period_;
}
void ASimModeWorldBase::setPhysicsLoopPeriod(long long period)
{
    physics_loop_period_ = period;
}

std::unique_ptr<ASimModeWorldBase::PhysicsEngineBase> ASimModeWorldBase::createPhysicsEngine()
{
    std::unique_ptr<PhysicsEngineBase> physics_engine;
    std::string physics_engine_name = getSettings().physics_engine_name;
    if (physics_engine_name == "")
        physics_engine.reset(); //no physics engine
    else if (physics_engine_name == "FastPhysicsEngine") {
        msr::airlib::Settings fast_phys_settings;
        if (msr::airlib::Settings::singleton().getChild("FastPhysicsEngine", fast_phys_settings)) {
            physics_engine.reset(new msr::airlib::FastPhysicsEngine(fast_phys_settings.getBool("EnableGroundLock", true)));
        }
        else {
            physics_engine.reset(new msr::airlib::FastPhysicsEngine());
        }

        physics_engine->setWind(getSettings().wind);
        physics_engine->setExtForce(getSettings().ext_force);
    }
    else if (physics_engine_name == "ExternalPhysicsEngine") {
        physics_engine.reset(new msr::airlib::ExternalPhysicsEngine());
    }
    else {
        physics_engine.reset();
        UAirBlueprintLib::LogMessageString("Unrecognized physics engine name: ", physics_engine_name, LogDebugLevel::Failure);
    }

    return physics_engine;
}

bool ASimModeWorldBase::isPaused() const
{
    return physics_world_->isPaused();
}

void ASimModeWorldBase::pause(bool is_paused)
{
    physics_world_->pause(is_paused);
    ASimModeBase::pause(is_paused);
}

void ASimModeWorldBase::continueForTime(double seconds)
{
    int64 start_frame_number = UKismetSystemLibrary::GetFrameCount();
    if (physics_world_->isPaused()) {
        physics_world_->pause(false);
        UGameplayStatics::SetGamePaused(this->GetWorld(), false);
    }

    physics_world_->continueForTime(seconds);
    while (!physics_world_->isPaused()) {
        continue;
    }
    // wait if no new frame is renderd
    while (start_frame_number == UKismetSystemLibrary::GetFrameCount()) {
        continue;
    }
    UGameplayStatics::SetGamePaused(this->GetWorld(), true);
}

void ASimModeWorldBase::continueForFrames(uint32_t frames)
{
    if (physics_world_->isPaused()) {
        physics_world_->pause(false);
        UGameplayStatics::SetGamePaused(this->GetWorld(), false);
    }

    physics_world_->setFrameNumber((uint32_t)GFrameNumber);
    physics_world_->continueForFrames(frames);
    while (!physics_world_->isPaused()) {
        physics_world_->setFrameNumber((uint32_t)GFrameNumber);
    }
    UGameplayStatics::SetGamePaused(this->GetWorld(), true);
}

void ASimModeWorldBase::setWind(const msr::airlib::Vector3r& wind) const
{
    physics_engine_->setWind(wind);
}

void ASimModeWorldBase::setExtForce(const msr::airlib::Vector3r& ext_force) const
{
    physics_engine_->setExtForce(ext_force);
}

void ASimModeWorldBase::updateDebugReport(msr::airlib::StateReporterWrapper& debug_reporter)
{
    unused(debug_reporter);
    //we use custom debug reporting for this class
}

void ASimModeWorldBase::Tick(float DeltaSeconds)
{
    { //keep this lock as short as possible
        physics_world_->lock();

        physics_world_->enableStateReport(EnableReport);
        physics_world_->updateStateReport();

        for (auto& api : getApiProvider()->getVehicleSimApis()) {
            if (api->getVehicleSetting()->vehicle_type != AirSimSettings::kVehicleTypePhysXCar) {
                api->updateRenderedState(DeltaSeconds);
            }
        }
        physics_world_->unlock();
    }

     //perform any expensive rendering update outside of lock region
    for (auto& api : getApiProvider()->getVehicleSimApis()) {
        if (api->getVehicleSetting()->vehicle_type == AirSimSettings::kVehicleTypePhysXCar) {
            // Since the background thread is ignoring the car, 
            // the Game Thread must handle its rendered state update.
            api->updateRenderedState(DeltaSeconds);
        }
        api->updateRendering(DeltaSeconds);
    }

    Super::Tick(DeltaSeconds);
}

void ASimModeWorldBase::reset()
{
    UAirBlueprintLib::RunCommandOnGameThread([this]() {
        // Reset the background physics world (Drones)
        if (physics_world_)
            physics_world_->reset();

        // Manually reset all Cars
        for (auto& api : getApiProvider()->getVehicleSimApis()) {
            if (api->getVehicleSetting()->vehicle_type == AirSimSettings::kVehicleTypePhysXCar) {
                api->reset();
            }
        }
        }, true);
}

std::string ASimModeWorldBase::getDebugReport()
{
    return physics_world_->getDebugReport();
}
