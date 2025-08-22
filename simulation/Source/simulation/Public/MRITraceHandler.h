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
		const UMaterialInstance *material,  // T1, T2 [s]
		double TR,              // repetition time [ms]
		double TE,              // echo time [ms]
		double alphaDeg = 20,   // flip angle [degrees]
		double Gd = 0.0,        // Gadolinium concentration [mM]
		double R1 = 4.5,        // Gd relaxivity T1 [1/(s*mM)]
		double R2 = 5.0,        // Gd relaxivity T2 [1/(s*mM)]
		double M0 = 1.0         // Proton density / scaling
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

	bool MakePairs(
		const TArray<FHitResult>& forwardHits,
		const TArray<FHitResult>& reverseHits,
		TArray<TPair<FHitResult*, FHitResult*>>& outHitPairs
	);
};
