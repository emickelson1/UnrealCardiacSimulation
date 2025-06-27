// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MRITraceHandler.generated.h"

/**
 * 
 */
UCLASS()
class SIMULATION_API UMRITraceHandler : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Capture")
	void MRIScan(
		const int32 countX,
		const int32 countY,
		const int32 countZ,
		const FVector& minBounds, 
		const FVector& maxBounds, 
		const float TE,
		const float TR,
		const float R1,
		const float Gd,
		TArray<int32>& volume, 
		TArray<int32>& segmentation
	);

private:
	UFUNCTION(BlueprintCallable, Category = "Capture")
	int32 ComputeVoxelValue(
		const UMaterialInstance *material,
		const float TE, 
		const float TR,
		const float R1,
		const float Gd
	);
};
