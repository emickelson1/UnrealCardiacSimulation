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
		TArray<uint8>& volume, 
		TArray<uint8>& segmentation
	);

private:
	uint8 ComputeVoxelValue(
		const UMaterialInstance *material,
		const float TE, 
		const float TR,
		const float R1,
		const float Gd
	);

	bool DoLineTrace(
		const FVector& start, 
		const FVector& end, 
		const int substeps,
		const FCollisionObjectQueryParams& queryParams, 
		const FCollisionQueryParams& collisionParams,
		TArray<FHitResult>& accForwardHits,
		TArray<FHitResult>& accReverseHits
	);

	bool DoAdditionalDetailTrace(
		const FVector& start, 
		const FVector& end, 
		const FCollisionObjectQueryParams& queryParams, 
		const FCollisionQueryParams& collisionParams,
		FHitResult& outHitResult
	);

	TArray<TPair<FHitResult*, FHitResult*>> MakePairs(
		const TArray<FHitResult>& forwardHits,
		const TArray<FHitResult>& reverseHits
	);
};
