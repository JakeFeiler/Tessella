# Tessella
Implementation of Tessella by Michael Lefkowitz

Welcome to Tessella! To win the game, you must be the first to capture 4 of your opponents 7 tokens..

The board is positioned in a diamond configuration, each player begins with their 7 tokens on the closest octagon to them on the outer ring. 
Player 1, for instance, starts with tokens on shapes 1, 2, 3, 4, 6, 11, & 16.

Every turn you have 2 options: move a token, or capture an enemy's token. You must take one of these two actions
Moving a token simply involves moving a token to an adjacent, unoccupied shape (it must share a side).
A token on a central octagon, for instance, could move to up to 8 shapes. A token on a square could move to up to 4.

Capturing tokens happen along rows, columns, and diagonals of the gameboard.
In order to capture, a sequence must exist on one of these straight lines of: your token, your token, enemy token.
Unoccupied shapes are allowed in between, and more tokens may come before or after this sequence, but this precise sequence must exist somewhere on the row/column/diagonal.

To capture, the middle token moves to occupy the enemy token's position on the gameboard. The enemy token is then removed.
Think of it like a queen in chess, or perhaps, like the back token as the gun barrel, the middle token as the bullet, and your opponent's token as the target.

As an example, say your opponent had tokens on shapes 5, 38, and 21 while you had tokens on shapes 13 and 35.
Two sequences of <you, you, opponent> exist on this row.
You could either use 13 to capture on 5 (35 is the 'barrel'), or use 35 to capture on 38 (13 is the 'barrel').
Note that if it was your opponent's turn, they could use 38 to capture on 35, as they also have the needed sequence (21 is the 'barrel').

You can also capture along the 4 rows and 4 columns of the 4x4 grid of squares, even though the squares do not share sides.
That grid's diagonals are already part of rows and columns of alternating octagons and squares, so you may not ignore the octagons to make captures in those directions.
Note that in the board's diamond orientation, the diagonals appear as the horizontal and vertical rows, and vice-versa.



Have fun!

To play, run play.py with your designated python3 version.

The board configurtation:
<pre>
                                    |---|
                                   /     \
                                  /       \
                                 /         \
                                |           |
                                |     25    |
                            |---|           |---|
                           /     \         /     \
                          /       \       /       \
                         /         \     /         \
                        |           |---|           |
                        |     20    | 41|     24    |
                    |---|           |---|           |---|
                   /     \         /     \         /     \
                  /       \       /       \       /       \
                 /         \     /         \     /         \
                |           |---|           |---|           |
                |     15    | 37|     19    | 40|     23    |
            |---|           |---|           |---|           |---|
           /     \         /     \         /     \         /     \
          /       \       /       \       /       \       /       \
         /         \     /         \     /         \     /         \
        |           |---|           |---|           |---|           |
        |     10    | 33|     14    | 36|     18    | 39|     22    |
    |---|           |---|           |---|           |---|           |---|
   /     \         /     \         /     \         /     \         /     \
  /       \       /       \       /       \       /       \       /       \
 /         \     /         \     /         \     /         \     /         \
|           |---|           |---|           |---|           |---|           |
|     5     | 29|     9     | 32|     13    | 35|     17    | 38|     21    |
|           |---|           |---|           |---|           |---|           |
 \         /     \         /     \         /     \         /     \         /
  \       /       \       /       \       /       \       /       \       /
   \     /         \     /         \     /         \     /         \     /
    |---|           |---|           |---|           |---|           |---|
        |     4     | 28|     8     | 31|     12    | 34|     16     |
        |           |---|           |---|           |---|           |
         \         /     \         /     \         /     \         /
          \       /       \       /       \       /       \       /
           \     /         \     /         \     /         \     /
            |---|           |---|           |---|           |---|
                |     3     | 27|     7     | 30|     11     |
                |           |---|           |---|           |
                 \         /     \         /     \         /
                  \       /       \       /       \       /
                   \     /         \     /         \     /
                    |---|           |---|           |---|
                        |     2     | 26|     6     |
                        |           |---|           |
                         \         /     \         /
                          \       /       \       /
                           \     /         \     /
                            |---|           |---|
                                |     1     |
                                |           |
                                 \         /
                                  \       /
                                   \     /
                                    |---|                                

</pre>

