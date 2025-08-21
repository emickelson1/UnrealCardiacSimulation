// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "ForceGarbageCollection.generated.h"

/**
 * 
 */
UCLASS()
class SIMULATION_API UForceGarbageCollection : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Memory")
	void ForceGarbageCollection();
};
