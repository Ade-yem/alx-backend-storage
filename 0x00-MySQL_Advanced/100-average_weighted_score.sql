--  creates a stored procedure ComputeAverageWeightedScoreForUser that
-- computes and store the average weighted score for a student

DELIMITER $$
DROP PROCEDURE IF EXISTS `ComputeAverageWeightedScoreForUser`$$
CREATE PROCEDURE ComputeAverageWeightedScoreForUser(user_id INT)
BEGIN
    DECLARE totalWeight INT;
    DECLARE totalProducts INT;
    DECLARE weightedAverage FLOAT;
    SELECT SUM(projects.weight * corrections.score) INTO totalProducts FROM corrections JOIN projects ON corrections.project_id = projects.id WHERE corrections.user_id = user_id;
    SELECT SUM(weight) INTO totalWeight FROM projects;

    -- Calculate the average weighted score
    IF totalWeight > 0 THEN
        SET weightedAverage = totalProducts / totalWeight;
    ELSE
        SET weightedAverage = NULL;
    END IF;
    
    -- Update the users table with the average score
    UPDATE users
    SET average_score = weightedAverage
    WHERE users.id = user_id;
END$$
DELIMITER ;
