from visual import *
from random import random
import time

#constants
scene.autoscale = false;
scene.height = 800;
scene.width = 800;
arenaSize = 20;
scene.range = arenaSize-2;
G = 6.67e-11;
pi = 3.14159265;
E_naught = 8.854187e-12;
K_e = 1 / ((4*pi)*E_naught);
g = 9.81; #m/s^2
dt = 0.01;
spring_relaxed_len = 0.654;
mass_Ship = 5;
mass_bullet = 0.1;
v_Ship = vector(0,0,0);
k_spring = 7.5; #7.5 N/m
pick = None;
global numShots;
numShots = 0;
global bullet;
bullet = [];
numAsteroids = 10; #start with five asteroids around the outer edges w/ random p
numCurrAst = 5; #will update this to keep track of how many destroyed
global astList;
astList = [];
theta = 0;
max_boosters = 10; #for evasive maneuvers

playerPoints = 0; #the score is equal to the health points of the destroyed asteroids!
numDestroyed = 0;

k_bullet = 50; #standard bullet does 50 damage on normal
hurtFactor = 0.5;
damageFactor = (1 / hurtFactor); #bullet damage inversely proportional to health damage

big_ind = 0;
med_ind = 0;
small_ind = 0;
#bool fired = False; #start it false - use this for determining the timer

global playerHealth;
playerHealth = 1000; #the health of the player in Joules

smallAst = []; #array for small asteroids to keep track of their health
medAst = [];
bigAst = [];
#array of all the big asteroids too keep track of their health
#bigger asteroids can take more damage before being split / destroyed


redShip = arrow(axis = (1, 0, 0), color = color.red, shaftwidth = 0.5);
redShip.pos.x = 0;
redShip.pos.y = 0;
redShip.p = mass_Ship * v_Ship;
redShip.m = mass_Ship;

omega = (2*pi / 1.5); #in radians / sec
r = mag(redShip.axis);
inertia = mass_Ship * (r*r); #mR^2
redShip.l = inertia*omega; #vector angular momentum L

#spring = helix (pos = (0, 1.305, 0), axis = (0,0.01,0), radius = 0.02, thickness = 0.01, color = color.cyan);

def spawnAsteroid():
    global med_ind;
    global small_ind;
    global big_ind;
    newAsteroid = sphere(radius = randomValue(0.2,1));
    
    x = randomValue(-1,1)
    if x < 0: #go right - it spawns on left side of scene
        newAsteroid.pos.x = x - (arenaSize-2); #the asteroid will be placed between arenaSize and arenaSize-2
        v_hat_x = cos(randomValue(0,pi/2)); #v in direction of opposite side, use a random angle of projection
    elif x >= 0: #go left
        newAsteroid.pos.x = x + (arenaSize-2);
        v_hat_x = cos(randomValue(pi/2,pi));
        
    y = randomValue(-1,1)
    if y < 0: #go up
        newAsteroid.pos.y = y - (arenaSize-2);
        v_hat_y = sin(randomValue(0,pi/2));
    elif y >= 0: #go down
        newAsteroid.pos.y = y + (arenaSize-2);
        v_hat_y = sin(randomValue(pi/2,pi));

    v_hat_ast = vector(v_hat_x, v_hat_y, 0);

    #below: scale the velocities and masses with the radii assigned
    #asteroids come in small, medium, and big sizes

    if (newAsteroid.radius >= 0.7):
        v_mag_ast = vector(randomValue(0.1,5),randomValue(0.1,5),0);
        v_ast = mag(v_mag_ast) * v_hat_ast; #get the random velocity vector
        newAsteroid.m = randomValue(6.5, 10); #random mass for appropriate radii
        newAsteroid.index = big_ind;
        newAsteroid.health = 300;
        newAsteroid.healthOrig = 200;
        big_ind += 1;
        #finally set the momentum
        newAsteroid.p = v_ast * newAsteroid.m;
        bigAst.append(newAsteroid);
    elif (newAsteroid.radius <= 0.39):
        v_mag_ast = vector(randomValue(3.5,7),randomValue(3.5,7),0);
        v_ast = mag(v_mag_ast) * v_hat_ast; #get the random velocity vector
        newAsteroid.m = randomValue(0.1,3.5);
        newAsteroid.p = v_ast * newAsteroid.m;
        newAsteroid.index = small_ind;
        newAsteroid.health = 50;
        newAsteroid.healthOrig = 50; #for scorekeeping purposes
        small_ind += 1;
        smallAst.append(newAsteroid);
    else:
        v_mag_ast = vector(randomValue(2.5,6),randomValue(2.5,6),0);
        v_ast = mag(v_mag_ast) * v_hat_ast; #get the random velocity vector
        newAsteroid.m = randomValue(3.6,6.4);
        newAsteroid.p = v_ast * newAsteroid.m;
        newAsteroid.index = med_ind;
        newAsteroid.health = 200;
        newAsteroid.healthOrig = 100;
        med_ind += 1;
        medAst.append(newAsteroid);

    return newAsteroid;

def destroyAsteroid(asteroid, index):
    global playerPoints;
    global numDestroyed;
    astList[index].visible = False;
    #del astList[index];
    astList[index].pos.x = 1000;
    astList.remove(astList[index]);
    #replace it
    astList.append(spawnAsteroid());
    #assign points
    playerPoints += asteroid.healthOrig;
    numDestroyed += 1;

def buildList():
    i = 0;
    while (i < numAsteroids):
        astList.append(spawnAsteroid());
        i += 1;
    
def randomValue(low, high):
    return (high-low)*random() + low;

def checkForUserInteraction():
    v_Ship_x = redShip.p.x / mass_Ship;
    v_Ship_y = redShip.p.y / mass_Ship;
    acceleration = 30;
    thrust = mass_Ship * acceleration; #thrust force
    #theta = 0;
    global theta;
    d_theta = 10 * (pi / 180);
    
    #use angular momentum principle
    #omega = (2*pi/1.5); #in radians / sec
    r = mag(redShip.axis);
    #inertia = mass_Ship * (r*r); #mR^2
    x_acceleration = vector(0.2,0,0);
    y_acceleration = vector(0,0.2,0);
    
    if scene.kb.keys:
        key = scene.kb.getkey();
        if (key == 'j'): #calculate torque and angular impulse
            #f_rot = vector(10, 10, 0); #newton force for rotation
            #torque = cross(redShip.axis, f_rot); #cross product gives torque
            #redShip.l += torque*dt;
            #axis_hat = cross( norm(redShip.axis), omega );
            #redShip.axis += axis_hat * dt;
            #redShip.axis.x = mag(redShip.axis) * cos(omega*dt);
            #redShip.axis.y = mag(redShip.axis) * sin(omega*dt);
            theta += d_theta;
            redShip.axis.y = mag(redShip.axis)*sin(theta);
            redShip.axis.x = mag(redShip.axis)*cos(theta);
        if (key == 'k'): #reverse rotate
            theta -= d_theta;
            redShip.axis.y = mag(redShip.axis)*sin(theta);
            redShip.axis.x = mag(redShip.axis)*cos(theta);
        if (key == 'a'):
            redShip.p.x -= thrust*dt;
        if (key == 'd'):
            redShip.p.x += thrust*dt;
        if (key == 'w'):
            redShip.p.y += thrust*dt;
        if (key == 's'):
            redShip.p.y -= thrust*dt;
        if (key == 'g'): #fire boosters, subtract amount available
            global max_boosters;
            if (max_boosters > 0):
                direction = norm(redShip.p);
                boosted = 2*mag(redShip.p);
                redShip.p = boosted*direction;
                max_boosters -= 1;
            else:
                print ("WARNING: NO BOOSTER CELLS REMAINING!");
        if (key == 'f'):
            fireAmmo();
        if (key == 'b'):
            #if(redShip.p.x - 3*thrust*dt > 0 and redShip.p.y - 3*thrust*dt > 0):
                #redShip.p.x -= 3*thrust*dt; redShip.p.y -= 3*thrust*dt;
            #elif(redShip.p.x - 2*thrust*dt > 0 and redShip.p.y - 2*thrust*dt > 0):
                #redShip.p.x -= 2*thrust*dt; redShip.p.y -= 2*thrust*dt;
            #elif(redShip.p.x - thrust*dt > 0 and redShip.p.y - thrust*dt > 0):
                #redShip.p.x -= thrust*dt; redShip.p.y -= thrust*dt;
            #else:
                redShip.p.x -= redShip.p.x*dt*50; redShip.p.y -= redShip.p.y*dt*50;
        if (key == 'p'):
            pause();


def pause():
    while True:
        rate(50)
        if scene.mouse.events:
            m = scene.mouse.getevent()
            if m.click == 'left': return
        #elif scene.kb.keys:
            #k = scene.kb.getkey()
            #return

def checkWalls():
    i = 0;
    #bool continue = True;
    while (i < numAsteroids):
        if (astList[i].pos.x + astList[i].radius > arenaSize):
            astList[i].p.x = -1*abs(astList[i].p.x);
        if(astList[i].pos.y + astList[i].radius > arenaSize):
            astList[i].p.y = -1*abs(astList[i].p.y);
        if(astList[i].pos.x + astList[i].radius < -arenaSize):
            astList[i].p.x = 1*abs(astList[i].p.x);
        if(astList[i].pos.y + astList[i].radius < -arenaSize):
            astList[i].p.y = 1*abs(astList[i].p.y);
        i += 1;
            
def checkEveryCollision():
    global numShots;
    i = 0;
    while i < numAsteroids:
        j = i+1;
        while j < numAsteroids:
               checkCollision(astList[i], astList[j])
               j += 1;
        checkPlayerHit(astList[i], i); #only need to do this in outer loop
        i += 1;
    x = 0;
    while x < numShots:
        y = 0;
        while y < numAsteroids:
            if(x < numShots):
                checkBulletHit(bullet[x], x, astList[y], y);#see if bullets hit
                y += 1;
            else:
                break; break;
        x += 1;


def checkCollision(ast1,ast2):
    r = ast1.pos-ast2.pos; #distance between their centers
    magr = mag(r);
    vrel = (ast1.p/ast1.m) - (ast2.p/ast2.m); #tells you how one is moving in comparison to another
    #we need to know if the dot product is pos or neg to tell if they are moving toward each other
    
    if (magr < ast1.radius + ast2.radius and dot(vrel,r) < 0) : #if its less than their radii, collision has happened
        vcm = (ast1.p + ast2.p) / (ast1.m + ast2.m);
        rhat = norm(ast1.pos - ast2.pos); #get the direction vector
        ast1.p = ast1.p - 2*ast1.m*rhat*dot((ast1.p/ast1.m) - vcm, rhat);
        ast2.p = ast2.p - 2*ast2.m*rhat*dot((ast2.p/ast2.m) - vcm, rhat);

def checkBulletHit(blet, b_index, ast, ast_index): #check if we have a collision!
    global numShots;
    global playerPoints;
    r = blet.pos - ast.pos;
    mag_r = mag(r);

    v_rel = (blet.p/mass_bullet) - (ast.p/ast.m);

    if (mag_r < blet.radius + ast.radius and dot(v_rel,r) < 0): #if yes, collision!
        #destroy the asteroid and the bullet, but first store their momenta
        p_b = blet.p;
        p_ast = ast.p;
        #if(ast.radius <= 0.39):
        if (ast.health - (damageFactor*k_bullet) <= 0):
            ast.health -= damageFactor*k_bullet;
            destroyAsteroid(ast,ast_index); #completely destroy it
        else:
            ast.health -= damageFactor*k_bullet;
            ast.p += -1*blet.p; #conserve the momentum of the collision
        blet.visible = False;
        blet.pos.x += 100; #move it off screen and out of harms way
        bullet.remove(bullet[b_index]);
        numShots -= 1;
        print ("SCORE: ", playerPoints);
        '''elif(ast.radius > 0.5 and ast.radius < 0.7): #smaller mag of damage, split it
            destroyAsteroid(ast,ast_index);
            #splitAsteroid(ast, p_b+p_ast); #args are object, and sum of momenta of objects
            blet.visible = False;
            blet.pos.x += 100;
            bullet.remove(bullet[b_index]);
            numShots -= 1;'''
        

def fireAmmo():
    global numShots;
    b_pos = redShip.pos + (norm(redShip.axis)*mag(redShip.axis));
    bullet.append(sphere(radius = 0.1, pos = b_pos, color = color.cyan));
    #get firing direction - in line with the axis
    bullet_v_hat = norm(redShip.axis);
    bullet[numShots].v = 7*bullet_v_hat; #7 m/s bullet speed
    bullet[numShots].m = mass_bullet;
    bullet[numShots].p = mass_bullet*bullet[numShots].v;
    #update the number of fired shots
    numShots += 1;

def moveAsteroids():
    i = 0;
    while (i < numAsteroids):
        astList[i].pos += (astList[i].p / astList[i].m)*dt;
        i += 1;

def forceGrav(obj1, obj2):
    r = obj1.pos - obj2.pos; #distance between them
    mag_r = mag(r);
    r_hat = norm(r);

    Fgrav = -(G * (obj1.m*obj2.m) / (mag_r*mag_r)) * r_hat; #vector force of gravity
    return Fgrav;
    

#determine the gravitational force between all the asteroids and the ship
def checkGravity():
    i = 0;
    while (i < numAsteroids): #first for the asteroids
        j = i+1;
        while (j < numAsteroids):
            Fgij = forceGrav(astList[i], astList[j]);
            Fgji = forceGrav(astList[j], astList[i]);
            astList[j].p += Fgji*dt; #fg by j on i
            astList[i].p += Fgij*dt; #fg by i on j
            j += 1;
        i+= 1;
        
    x = 0;
    while (x < numAsteroids):
        Fgsx = forceGrav(redShip, astList[x]);
        Fgxs = forceGrav(astList[x], redShip);
        redShip.p += Fgxs*dt; #fg by ship on ast
        astList[x].p += Fgsx*dt;
        x += 1;

def updateBullets():
    global numShots;
    i = 0;
    while i < numShots:
        bullet[i].pos += (bullet[i].p / mass_bullet)*dt;
        #check if offscreen, delete it necessary
        if (bullet[i].pos.x > arenaSize+10 or bullet[i].pos.x < -arenaSize-10
            or bullet[i].pos.y > arenaSize+10 or bullet[i].pos.y < -arenaSize-10):
            #delete the object, then move every element back a position to replace
            '''x = numShots; #index of last shot fired
            if (i>1): #needs to be at least one more bullet for this to work
                del bullet[i];
                while (x > i+1):
                    bullet[x-1] = bullet[x];
                    numShots -= 1;
                    del bullet[x];
                    x -= 1;'''
            #copy all elements except the object to be remove, decrement numShots
            '''newList = [];
            x = 0;
            while x < numShots:
                if( x != i): #don't copy the element being deleted
                    newList.append(bullet[x]);
                    del bullet[x];
                x += 1;
            numShots -= 1;
            j = 0;
            while j < numShots:'''
            #obj = weakref.ref(bullet.remove(bullet[i]));
            #del obj;
            bullet[i].visible = False;
            bullet.remove(bullet[i])
            numShots -= 1;
                
        i+=1;


#def subPlayerHealth(val): #val will be some fraction of the KE of the hitter
    #playerH
    

def checkPlayerHit(asteroid, index):
    global playerHealth;
    #r = norm(redShip.axis); #the direction of the arrow
    #mag_r = mag(redShip.axis); #the magnitude
    #x = redShip.pos.x; y = redShip.pos.y;
    
    #first check if axis is hit, then rest of ship
    #if ((x + mag_r)*r < (asteroid.pos + asteroid.radius) or
        #(y + (mag_r))*r < (asteroid.pos + asteroid.radius)): #if player hit
        #redShip.p -= asteroid.p; #contact forces equal and opposite, so change momentum
        #playerHealth -= (.5*((asteroid.p**2)/(2*asteroid.m))); #ratio is 1/2 KE of asteroid
        #destroyAsteroid(ast, index);
    r = redShip.pos-asteroid.pos; #distance between their centers
    magr = mag(r);
    vrel = (redShip.p/redShip.m) - (asteroid.p/asteroid.m); #tells you how one is moving in comparison to another
    #we need to know if the dot product is pos or neg to tell if they are moving toward each other
    
    if (magr < mag(redShip.axis) + asteroid.radius and dot(vrel,r) < 0):
    #if (redShip.pos.x < asteroid.pos.x + asteroid.radius or
        #redShip.pos.y < asteroid.pos.y):
        redShip.p += asteroid.p; #contact forces equal and opposite, so change momentum
        playerHealth -= (hurtFactor*((mag(asteroid.p)**2)/(2*asteroid.m))); #ratio is KE of asteroid * hurtFactor
        print ("CURRENT HP: ", playerHealth);
        destroyAsteroid(asteroid, index);

selection = "";
difficulty = "Normal";
done = True;

print ("Welcome to Elasteroids!");
print ("Please choose/enter a difficulty.\n");
'''while True:
    selection = input("E for easy, N for Normal, H for Heroic, L for Legendary.\n Selection: ");
    if (selection == 'e' or selection == 'E' or selection == 'n' or selection == 'N'
        or selection == 'h' or selection == 'H' or selection == 'l' or selection == 'L'):
        break; #break out if correct input
    else:
        print("Input error. Please try again: ");

if(selection == 'e' or selection == 'E'): difficulty = "Easy"; hurtFactor = 0.5;
if(selection == 'n' or selection == 'N'): difficulty = "Normal"; hurtFactor = 1;
if(selection == 'h' or selection == 'H'): difficulty = "Heroic"; hurtFactor = 1.5;
if(selection == 'l' or selection == 'L'): difficulty = "Legendary"; hurtFactor = 2.5;
print ("Your chosen difficulty: ", difficulty);
print ("\nGood Luck Bro!");

if(difficulty == "Easy"): numAsteroids = 7; print("\n\nYou will laugh as you crush this game.\n\n");
if(difficulty == "Normal"): numAsteroids = 11; print("\n\nYou will meet fair resistance, but a quick trigger finger will keep you safe.\n\n");
if(difficulty == "Heroic"): numAsteroids = 15; print("\n\nYour efforts shall be honorable, but this is a task in which few succeed.\n\n");
if(difficulty == "Legendary"): numAsteroids = 20; print("\n\nYou will not survive.\n\n");'''

#health starts at 1000
print ("CURRENT HP: ", playerHealth, '\n');

print ("Click on the game window to start!\n");
#pause();

buildList(); #initialize the array of asteroids

total = time.time();
final = time.time();
begin = time.time();

mag_axis = mag(redShip.axis);


while True:
    rate(1/dt);

    redShip.p.z = 0; #to prevent it from getting smaller
    redShip.pos.z = 0;
    redShip.axis = norm(redShip.axis)*mag_axis;

    #check here for player health and break loop / end game if <= 0
    if (playerHealth <= 0):
        final = time.time();
        total = final - begin; #get the total time played in seconds
        print ("\n\nGAME OVER!\n\n")
        #print ("Total time played: ", total, end=" seconds\n");
        print ("Final Score: ", playerPoints);
        print ("Number of Asteroids destroyed: ", numDestroyed);
        print ("\nThanks for playing Elasteroids!");
        break; #end the game
        
    #update position of ship if it is in scene range
    update_x = redShip.pos.x + (redShip.p.x/mass_Ship)*dt;
    update_y = redShip.pos.y + (redShip.p.y/mass_Ship)*dt;
    if (update_x > -1*abs(arenaSize-2) and update_x < arenaSize-2):
        redShip.pos.x += (redShip.p.x / mass_Ship)*dt;
    else:
        redShip.p.x = 0; #can't move left, act like there is a wall so p is lost

    if (update_y > -1*abs(arenaSize-2) and update_y < arenaSize-2):
        redShip.pos.y += (redShip.p.y / mass_Ship)*dt;
    else:
        redShip.p.y = 0;
        
    updateBullets(); #update positions and delete if they go out of bounds

    #calculate net forces and update momentum - only considering gravity
    checkGravity();
    moveAsteroids();
        
    #user interactions with mouse and kb
    if scene.mouse.events: 
        m1 = scene.mouse.getevent() # get event
        if m1.drag and m1.pick == redShip: # if touched ball
            drag_pos = m1.pickpos # where on the ball
            pick = m1.pick # pick now true (not None) 
        elif m1.drop: # released at end of drag
            pick = None # end dragging (None is false)
    if pick:
        # project onto xy plane, even if scene rotated:
        new_pos = scene.mouse.project(normal=(0,0,1)) 
        if new_pos != drag_pos: # if mouse has moved
            # offset for where the ball was clicked:
            #pick.axis = new_pos - drag_pos
            direction = new_pos - pick.axis
            d_r = norm(direction); #get the direction vector
            #print(d_r)
            pick.axis = mag(pick.axis) * d_r; #update the direction of the axis, not its magnitude
            drag_pos = new_pos # update drag position
                
    checkForUserInteraction(); #will update momentum of ship
    checkEveryCollision();
    checkWalls();
        
    #allow spring to follow ball
    #spring.axis = redShip.pos - spring.pos;

    #find spring stretch
    #stretch = mag(spring.axis) - spring_relaxed_len;

    #find forces for springs, gravity
    #force_spring = k_spring*stretch*norm(-spring.axis);
    #force_grav = vector(0,-mass_Ship*g,0);

    #f_net = force_grav+force_spring;

    #redShip.p += f_net*dt;


'''while True:
    PlayGame();
    play = input("Would you like to play again? (Y/N): ");
    if (play == "N" or play == "n"):
        break;

scene.exit = True; #close the main game window if finished'''
