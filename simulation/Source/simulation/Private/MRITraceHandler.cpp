// Fill out your copyright notice in the Description page of Project Settings.


#include "MRITraceHandler.h"
#include <map>
#include "Algo/Reverse.h"

void UMRITraceHandler::MRIScan(
    const int32 sliceCount, 
    const int32 sliceSize, 
    const FVector& minBounds, 
    const FVector& maxBounds, 
    TArray<uint8>& slices, 
    TArray<uint8>& segmentations
)
{
    // Initialize increment values
	const float zIncrement = (maxBounds.Z - minBounds.Z) / sliceCount;
    const float xIncrement = (maxBounds.X - minBounds.X) / sliceSize;
    float scale = (maxBounds.Y - minBounds.Y) / sliceSize;

    // Define slices and segmentation array size
    slices.SetNum(sliceCount * sliceSize * sliceSize);
    segmentations.SetNum(sliceCount * sliceSize * sliceSize);

    // Initialize line trace parameters
    TArray<FHitResult> forwardHits;
    TArray<FHitResult> backwardHits;
    FVector start = minBounds;
    FVector end = minBounds;
    end.Y = maxBounds.Y;
    const FCollisionQueryParams collisionParams = FCollisionQueryParams(
        FName(TEXT("MRITrace")), 
        true, 
        nullptr // No owner
    );


    // Create each slice by line tracing repetitively
    for (int32 sliceIndex = 0; sliceIndex < sliceCount; ++sliceIndex)
    {
        // Line trace at each X position
        for (int32 xIndex = 0; xIndex < sliceSize; ++xIndex){
            // Forward trace (get hits on forward faces of colliders)
            bool forwardTrace = GetWorld()->LineTraceMultiByChannel(
                forwardHits,
                start,
                end,
                ECC_Visibility,
                collisionParams
            );

            // Draw line
            DrawDebugLine(
                GetWorld(),
                start,
                end,
                FColor::Green,
                true,
                5.0f,
                0,
                1.0f
            );

            // If the forward trace did not hit anything, skip to the next linetrace
            if (!forwardTrace) {
                start.X += xIncrement;
                end.X += xIncrement;
                continue;
            }

            // Backward trace and reverse results (get hits on back faces of colliders))
            bool backwardTrace = GetWorld()->LineTraceMultiByChannel(
                backwardHits,
                end,
                start,
                ECC_Visibility,
                collisionParams
            );
            Algo::Reverse(backwardHits);

            // Iterate through hit objects, use the distances between front and back hits to fill slices and segmentations
            for (FHitResult &forwardHit : forwardHits){
                // Find the object hit by this forward trace
                UObject *hitObject = forwardHit.GetActor();

                // Find the corresponding backward hit, then remove it from the backward hits array
                FHitResult *backwardHit = nullptr;
                for (FHitResult &backwardHitCandidate : backwardHits){
                    if (backwardHitCandidate.GetActor() == hitObject) {
                        backwardHit = &backwardHitCandidate;
                        break;
                    }
                }
                backwardHits.Remove(*backwardHit);

                // Fill slice indices between start and end
                int32 startYIndex = forwardHits[0].Distance / scale;
                int32 endYIndex = backwardHit->Distance / scale;
                for (int32 yIndex = startYIndex; yIndex < endYIndex; ++yIndex) {
                    int32 index = (sliceIndex * sliceSize * sliceSize) + (xIndex * sliceSize) + yIndex;
                    if (index < slices.Num()) {
                        slices[index] = forwardHits[0].Distance;
                        segmentations[index] = 255; // Assuming segmentation is binary
                    }
                }
            }

            // Increment x values for the next iteration
            forwardHits.Empty();
            backwardHits.Empty();
            start.X += xIncrement;
            end.X += xIncrement;
        }

        // Reset for the next iteration
        start.X = minBounds.X;
        end.X = maxBounds.X;
        start.Z += zIncrement;
        end.Z += zIncrement;
    }
}
